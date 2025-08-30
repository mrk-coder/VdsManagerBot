# handlers/monitoring.py
from aiogram import Router, types
from utils.system_monitor import get_system_status, get_logs
from database.database import is_user_allowed, log_action

router = Router()

@router.message(lambda message: message.text == "/status")
async def status_handler(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    log_action(message.from_user.id, message.from_user.username or "Unknown", "/status", "Просмотр статуса сервера")

    status = get_system_status()
    response = (
        f"💻 *Статус сервера:*\n"
        f"🔹 CPU: {status['cpu']}%\n"
        f"🔹 RAM: {status['memory']}\n"
        f"🔹 Диск: {status['disk']}\n"
        f"🔹 Аптайм: {status['uptime']}\n"
        f"🔹 IP: `{status['ip']}`"
    )
    await message.answer(response, parse_mode="Markdown")

@router.message(lambda message: message.text.startswith("/logs"))
async def logs_handler(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    log_action(message.from_user.id, message.from_user.username or "Unknown", "/logs", f"Просмотр логов")

    try:
        lines = int(message.text.split()[1]) if len(message.text.split()) > 1 else 50
        # Ограничиваем количество строк для безопасности
        lines = min(lines, 200)
    except ValueError:
        lines = 50

    logs = get_logs(lines)
    
    # Обрезаем слишком длинные сообщения
    if len(logs) > 4000:
        logs = logs[:4000] + "\n... (вывод обрезан)"
    
    try:
        await message.answer(f"📄 Последние {lines} строк логов:\n```\n{logs}\n```", parse_mode="MarkdownV2")
    except:
        # Если MarkdownV2 не работает, пробуем обычный текст
        await message.answer(f"📄 Последние {lines} строк логов:\n```\n{logs}\n```", parse_mode="Markdown")
