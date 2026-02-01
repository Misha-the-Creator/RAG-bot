import os
from aiogram import F
from aiogram import Bot
import httpx
from aiogram import Router
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.filters import Command
from rag_bot.logic.keyboards import main_key
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

# Модуль-обработчик входящих сообщений

router = Router()

class Reg(StatesGroup):
    waiting_for_file = State()
    waiting_for_query = State()


@router.message(Command("start"))
async def handle_start(message: Message):
    await message.reply("Привет, что нужно сделать?",
                        reply_markup=main_key)

@router.message(F.text == 'Загрузить файл в базу знаний 📥')
async def handle_upload(message: Message, state: FSMContext):
    await message.answer("Ожидаю загрузки файла 🫣")
    await state.set_state(Reg.waiting_for_file)

@router.message(F.text == 'Дать ответ из базы 🗣️')
async def handle_query(message: Message, state: FSMContext):
    await message.answer("Введите ваш запрос к базе 🙂")
    await state.set_state(Reg.waiting_for_query)

@router.message(Reg.waiting_for_file)
async def handle_file(message: Message, state: FSMContext, bot):
    if message.document:
        try:
            await message.answer('Файл получен, отправлю в базу знаний...')
            
            file_id = message.document.file_id
            file_name = message.document.file_id
            file_size = message.document.file_id

            file = await bot.get_file(file_id)
            file_path = file.file_path
            downloaded_file = await bot.download_file(file_path)

            async with httpx.AsyncClient() as client:
                files = {
                    'file': (message.document.file_name, downloaded_file, 'application/pdf')
                }
                response = await client.post("http://ваш-апи:8000/upload-pdf/", files=files)
            
            if response.status_code == 200:
                await message.answer("✅ Файл успешно обработан и добавлен в базу!")
            else:
                await message.answer(f"❌ Ошибка сервера: {response.status_code}")
                
            await state.clear()