# handlers/user_management.py
from aiogram import Router, types
from utils.security import is_admin
import subprocess
import logging

router = Router()

@router.message(lambda message: message.text.startswith("/adduser"))
async def add_user(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администратор может управлять пользователями.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: `/adduser <username> [password]`\nЕсли пароль не указан, он будет сгенерирован.", parse_mode="Markdown")
            return

        username = parts[1]
        password = parts[2] if len(parts) > 2 else None

        # Создание пользователя
        cmd_create = ["sudo", "useradd", "-m", "-s", "/bin/bash", username]
        result_create = subprocess.run(cmd_create, capture_output=True, text=True)

        if result_create.returncode != 0:
            if "already exists" in result_create.stderr:
                await message.answer(f"⚠️ Пользователь `{username}` уже существует.", parse_mode="Markdown")
            else:
                await message.answer(f"❌ Ошибка создания пользователя: {result_create.stderr}")
            return

        # Установка пароля
        if password:
            cmd_pass = f"echo '{username}:{password}' | sudo chpasswd"
            result_pass = subprocess.run(cmd_pass, shell=True, capture_output=True, text=True)
            if result_pass.returncode != 0:
                await message.answer(f"⚠️ Пользователь создан, но ошибка установки пароля: {result_pass.stderr}")
                return
            else:
                await message.answer(f"✅ Пользователь `{username}` создан и пароль установлен.", parse_mode="Markdown")
        else:
            # Генерация случайного пароля (простой пример)
            import random, string
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            cmd_pass = f"echo '{username}:{password}' | sudo chpasswd"
            result_pass = subprocess.run(cmd_pass, shell=True, capture_output=True, text=True)
            if result_pass.returncode != 0:
                await message.answer(f"⚠️ Пользователь создан, но ошибка установки пароля: {result_pass.stderr}")
                return
            else:
                # Отправляем пароль в приватном сообщении или как-то иначе безопасно
                await message.answer(f"✅ Пользователь `{username}` создан.\n🔑 Пароль: `{password}` (сообщите пользователю безопасно!)", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка в /adduser: {e}")
        await message.answer(f"❌ Ошибка: {e}")

@router.message(lambda message: message.text.startswith("/deluser"))
async def del_user(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администратор может управлять пользователями.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: `/deluser <username>`", parse_mode="Markdown")
            return

        username = parts[1]

        # Удаление пользователя и его домашней директории
        cmd_del = ["sudo", "userdel", "-r", username]
        result_del = subprocess.run(cmd_del, capture_output=True, text=True)

        if result_del.returncode != 0:
            if "does not exist" in result_del.stderr:
                await message.answer(f"⚠️ Пользователь `{username}` не существует.", parse_mode="Markdown")
            else:
                await message.answer(f"❌ Ошибка удаления пользователя: {result_del.stderr}")
            return

        await message.answer(f"✅ Пользователь `{username}` успешно удален.", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка в /deluser: {e}")
        await message.answer(f"❌ Ошибка: {e}")
