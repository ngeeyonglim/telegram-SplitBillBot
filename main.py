import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from src.bot.handlers import router
from dotenv import load_dotenv

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    print("SplitBillBot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
