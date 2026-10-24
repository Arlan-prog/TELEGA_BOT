import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from app.handlers import router


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it to your .env file.")

    async with Bot(token=TOKEN) as bot:
        dispatcher = Dispatcher()
        dispatcher.include_router(router)
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="get_help", description="Show help"),
                BotCommand(command="get_news", description="Get news"),
                BotCommand(command="settings", description="Open settings"),
            ]
        )
        await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
