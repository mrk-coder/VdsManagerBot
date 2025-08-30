# handlers/services.py
from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.security import is_user_allowed, is_admin
import subprocess

router = Router()

@router.message(lambda message: message.text == "/services")
async def list_services(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    try:
        output = subprocess.check_output(["systemctl", "list-units", "--type=service", "--state=running"], text=True)
        lines = output.splitlines()[1:11]  # Первые 10 сервисов
        services = [line.split()[0] for line in lines if line]

        builder = InlineKeyboardBuilder()
        for svc in services:
            builder.button(text=svc, callback_data=f"svc_{svc}")
        builder.adjust(2)

        await message.answer("⚙️ Активные сервисы:", reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.callback_query(lambda c: c.data.startswith("svc_"))
async def service_action(callback: types.CallbackQuery):
    service = callback.data.split("_")[1]
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Перезапустить", callback_data=f"restart_{service}")
    builder.button(text="⏹ Остановить", callback_data=f"stop_{service}")
    builder.button(text="▶️ Запустить", callback_data=f"start_{service}")
    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(2)

    await callback.message.edit_text(f"Выберите действие для сервиса `{service}`:", parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith(("restart_", "stop_", "start_")))
async def handle_service_action(callback: types.CallbackQuery):
    action, service = callback.data.split("_", 1)
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Только администратор может управлять сервисами.", show_alert=True)
        return

    try:
        if action == "restart":
            subprocess.run(["systemctl", "restart", service], check=True)
            await callback.message.edit_text(f"✅ Сервис `{service}` перезапущен.", parse_mode="Markdown")
        elif action == "stop":
            subprocess.run(["systemctl", "stop", service], check=True)
            await callback.message.edit_text(f"⏹ Сервис `{service}` остановлен.", parse_mode="Markdown")
        elif action == "start":
            subprocess.run(["systemctl", "start", service], check=True)
            await callback.message.edit_text(f"▶️ Сервис `{service}` запущен.", parse_mode="Markdown")
    except subprocess.CalledProcessError as e:
        await callback.message.edit_text(f"❌ Ошибка при выполнении команды: {e}")
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel")
async def cancel_action(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.answer()
