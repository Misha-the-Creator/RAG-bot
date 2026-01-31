import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


@dp.message(Command("start"))
async def handle_start(message: Message):
    await message.answer("Привет")

async def handler(event: dict, context):
    print(f'{event=}')
    print(f'{context=}')
    return {'statusCode': 200, 'body': ''}


async def main():
    await dp.start_polling(bot)


def run():
    asyncio.run(main())