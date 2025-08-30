# main.py
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from database.database import init_db
from handlers import admin, monitoring, services, system, network, backup, start_help, user_management
from utils.notifications import SystemMonitor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Инициализация базы данных...")
    init_db()
    
    logger.info("Запуск бота...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Добавляем роутеры
    dp.include_routers(
        start_help.router,
        admin.router,
        monitoring.router,
        services.router,
        system.router,
        network.router,
        backup.router,
	user_management.router
    )

    # Запускаем мониторинг в отдельной задаче
    monitor = SystemMonitor(bot)
    asyncio.create_task(monitor.start_monitoring())

    logger.info("Бот запущен и готов к работе")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
