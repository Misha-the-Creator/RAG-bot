import asyncio
from rag_bot.bot.logic.handlers import router, bot
from aiogram import Dispatcher
from dotenv import load_dotenv
load_dotenv()

dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')