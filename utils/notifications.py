# utils/notifications.py
import psutil
import asyncio
from config.config import ADMIN_ID
from database.database import is_user_allowed

class SystemMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.last_notification = {}
        self.thresholds = {
            'cpu': 80,      # % CPU
            'memory': 85,   # % RAM
            'disk': 90      # % диск
        }

    async def check_system_load(self):
        """Проверяет нагрузку на систему и отправляет уведомления"""
        try:
            # Проверяем CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['cpu']:
                await self.send_notification("cpu", f"⚠️ Высокая нагрузка CPU: {cpu_percent}%")

            # Проверяем память
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds['memory']:
                await self.send_notification("memory", f"⚠️ Высокое использование памяти: {memory.percent}%")

            # Проверяем диск
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.thresholds['disk']:
                await self.send_notification("disk", f"⚠️ Мало свободного места на диске: {disk_percent:.1f}%")

        except Exception as e:
            print(f"Ошибка мониторинга: {e}")

    async def send_notification(self, alert_type: str, message: str):
        """Отправляет уведомление админу, если прошло достаточно времени"""
        current_time = asyncio.get_event_loop().time()
        last_time = self.last_notification.get(alert_type, 0)
        
        # Отправляем уведомление не чаще чем раз в 10 минут
        if current_time - last_time > 600:  # 600 секунд = 10 минут
            try:
                await self.bot.send_message(ADMIN_ID, message)
                self.last_notification[alert_type] = current_time
            except Exception as e:
                print(f"Ошибка отправки уведомления: {e}")

    async def start_monitoring(self):
        """Запускает периодический мониторинг"""
        while True:
            await self.check_system_load()
            await asyncio.sleep(60)  # Проверяем каждую минуту
