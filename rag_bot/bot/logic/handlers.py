import os
import httpx
from aiogram import F
from aiogram import Bot
from aiogram import Router
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from rag_bot.backend.logger.logger_config import logger1
from rag_bot.bot.logic.keyboards import main_key, file_actions_key
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
api = os.getenv('ADDR')
logger1.debug(f'{api=}')

# Модуль-обработчик входящих сообщений

router = Router()

class Reg(StatesGroup):
    waiting_for_file = State()
    waiting_for_deleting = State()
    waiting_for_query = State()
    waiting_for_reading = State()


@router.message(Command("start"))
async def handle_start(message: Message):
    await message.reply("Привет, что нужно сделать?",
                        reply_markup=main_key)

@router.message(F.text == 'Работа с файлами 📝')
async def handle_file_menu(message: Message):
    await message.answer("Выберите действие:",
                         reply_markup=file_actions_key)

@router.message(F.text == 'Дать ответ из базы 🗣️')
async def handle_query(message: Message, state: FSMContext):
    await message.answer("Введите ваш запрос к базе 🙂")
    await state.set_state(Reg.waiting_for_query)

@router.message(F.text == 'Загрузить новый документ 📥')
async def handle_upload_action(message: Message, state: FSMContext):
    await message.answer("Ожидаю загрузки файла 🫣")
    logger1.info('В состоянии waiting_for_file')
    await state.set_state(Reg.waiting_for_file)

@router.message(F.text == 'Удалить документ 🗑️')
async def handle_delete_action(message: Message, state: FSMContext):
    await message.answer("Введите наименование файла для удаления")
    logger1.info('В состоянии waiting_for_deleting')
    await state.set_state(Reg.waiting_for_deleting)

@router.message(F.text == 'Назад к меню ⬅️')
async def handle_back_option(message: Message, state: FSMContext):
    await message.reply("Возвратились в начальное меню",
                        reply_markup=main_key)

@router.message(F.text == 'Посмотреть все загруженные документы 📚')
async def handle_reading(message: Message):
    try:
        logger1.debug('В блоке waiting_for_reading')
        await message.answer('Вот файлы из БД:')
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{api}/psql/get-data-from-psql/')      
            response.raise_for_status()
            response_data = response.json()
            filenames, sizes = response_data['msg']
            for filename, size in zip(filenames, sizes):
                logger1.debug(f'{filename=}')
                await message.answer(f'{filename} — {size} байт')
    except Exception as e:
        logger1.error(f'Произошла ошибка при получении данных: {e}')

@router.message(Reg.waiting_for_deleting)
async def handle_deleting(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        try:
            file_to_delete = message.text
            async with httpx.AsyncClient() as client:
                response = await client.delete(f'{api}/psql/delete-data-from-psql/{file_to_delete}')      
                response.raise_for_status()
                response_data = response.json()
                delete = response_data['delete']
                file_uuid = response_data['qdrant_uuid']
                logger1.debug(f'Удаляем {file_uuid=}')
                if delete:
                    response = await client.delete(f'{api}/qdrant/delete-data-from-qdrant/{file_uuid}')      
                    response.raise_for_status()
                    response_data = response.json()
                    delete = response_data['delete']
                    if delete:
                        await message.answer(f"Успешно удалили {file_to_delete} из базы знаний")
                    else:
                        await message.answer(f"Не получилось удалить {file_to_delete} из базы знаний")
        except Exception as e:
            logger1.error(f'Произошла ошибка при удалении данных: {e}')
            await state.clear()

@router.message(Reg.waiting_for_file)
async def handle_file(message: Message, state: FSMContext, bot: Bot):
    if message.document:
        try:
            await message.answer('Проверяю на наличие в БД...')
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            downloaded_file = await bot.download_file(file_path, timeout=1000)
            async with httpx.AsyncClient() as client:
                file = {'file': (message.document.file_name, downloaded_file, 'application/pdf')}
                response_1 = await client.post(f'{api}/psql/post-data-to-psql/', files=file)
                response_1.raise_for_status()
                response_1_data = response_1.json()
                if response_1_data['load']:
                    response_2 = await client.post(f"{api}/qdrant/post-data-to-qdrant/{response_1_data['file_id']}", files=file)
                    response_2.raise_for_status()
                    response_2_data = response_2.json()
                    if response_2_data['msg']:
                        await message.answer("✅ Файл успешно обработан и добавлен в базу!")
                    else:
                        await message.answer(f"❌ Ошибка сервера: {response_2.status_code}")
                else:
                     await message.answer("Извините, но такой документ уже содержится в базе\n\nСписок всех доступных документов можно посмотреть, нажав на *Посмотреть список всех загруженных документов 📚*", parse_mode="MarkdownV2")
            await state.clear()
        except Exception as e:
            logger1.error(f'Ошибка при подаче на ручку: {e}')
        finally:
            await state.clear()

@router.message(Reg.waiting_for_query)
async def handle_query_message(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        try:
            query = message.text
            async with httpx.AsyncClient() as client:
                resp = await client.get(f'{api}/qdrant/search-qdrant/{query}')
                resp.raise_for_status()
                resp = resp.json()

                top_answer = resp['search']

                await message.answer(f"{top_answer}")
        except Exception as e:
            logger1.error(f'Ошибка при sim_search: {e}')