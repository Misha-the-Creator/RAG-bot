from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from rag_bot.app.keyboards import main_key
from dotenv import load_dotenv
load_dotenv()

# Модуль-обработчик входящих сообщений

router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    await message.reply("Привет, что нужно сделать?",
                        reply_markup=main_key)