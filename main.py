import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from database.database import init_db
from handlers.other import other_router
from handlers.user import user_router
from keyboards.menu_commands import set_main_menu
from services.file_handling import prepare_book

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config_data
    config: Config = load_config()

    # Задаём базовую конфигурацию логирования
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )
    # Выводим в консоль информацию о начале запуска бота
    logger.info("Starting bot")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подготавливаем книгу
    logger.info("Preparing book")
    book = prepare_book("book/poems.txt")
    logger.info("The book is uploaded. Total pages: %d", len(book))

    # Инициализируем "базу данных"
    db: dict = init_db()

    # Сохраняем готовую книгу и "базу данных" в `workflow_data`
    dp.workflow_data.update(book=book, db=db)

    # Настраиваем главное меню команд бота
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(user_router)
    dp.include_router(other_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())