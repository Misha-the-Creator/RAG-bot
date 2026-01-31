import os
import asyncio
from rag_bot.app.handlers import router
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')