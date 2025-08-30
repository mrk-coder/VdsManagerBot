# handlers/admin.py
from aiogram import Router, types
from database.database import add_user, is_admin, log_action
import subprocess

router = Router()

@router.message(lambda message: message.text.startswith("/auth"))
async def auth_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администратор может добавлять пользователей.")
        return

    try:
        user_id = int(message.text.split()[1])
        add_user(user_id, is_admin=False)
        log_action(message.from_user.id, message.from_user.username or "Unknown", "/auth", f"Добавлен пользователь {user_id}")
        await message.answer(f"✅ Пользователь {user_id} добавлен в белый список.")
    except (IndexError, ValueError):
        await message.answer("❌ Использование: /auth <user_id>")

@router.message(lambda message: message.text.startswith("/exec"))
async def exec_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администратор может выполнять команды.")
        return

    cmd = message.text[len("/exec "):].strip()
    if not cmd:
        await message.answer("❌ Укажите команду. Пример: `/exec ls -la`", parse_mode="Markdown")
        return

    log_action(message.from_user.id, message.from_user.username or "Unknown", "/exec", f"Выполнена команда: {cmd}")

    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        if len(output) > 4000:
            output = output[:4000] + "\n... (вывод обрезан)"
        await message.answer(f"✅ Результат выполнения:\n```\n{output}\n```", parse_mode="MarkdownV2")
    except subprocess.CalledProcessError as e:
        await message.answer(f"❌ Ошибка выполнения:\n```\n{e.output[:4000] if e.output else 'Нет вывода'}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        await message.answer(f"❌ Неизвестная ошибка: {e}")
