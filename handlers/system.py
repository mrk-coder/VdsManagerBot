# handlers/system.py
from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.system_monitor import get_top_processes, kill_process
from database.database import is_user_allowed, is_admin, log_action

router = Router()

@router.message(lambda message: message.text == "/processes")
async def list_processes(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    log_action(message.from_user.id, message.from_user.username or "Unknown", "/processes", "Просмотр процессов")

    try:
        procs = get_top_processes(10)
        text = "📊 Топ 10 процессов по CPU:\n\n"
        builder = InlineKeyboardBuilder()

        for p in procs:
            text += f"`{p['pid']}` - {p['name']} ({p['cpu_percent']}% CPU)\n"
            builder.button(text=f"❌ {p['name']} ({p['pid']})", callback_data=f"kill_{p['pid']}")

        builder.button(text="🔄 Обновить", callback_data="refresh_procs")
        builder.button(text="❌ Закрыть", callback_data="close")
        builder.adjust(1)

        await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.callback_query(lambda c: c.data.startswith("kill_"))
async def kill_process_callback(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Только администратор может убивать процессы.", show_alert=True)
        return

    try:
        pid = int(callback.data.split("_")[1])
        success, result = kill_process(pid)
        
        if success:
            log_action(callback.from_user.id, callback.from_user.username or "Unknown", "kill_process", f"Убит процесс {pid}")
            await callback.message.edit_text(f"✅ Результат: {result}")
        else:
            await callback.message.edit_text(f"❌ Ошибка: {result}")
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")
    await callback.answer()

@router.callback_query(lambda c: c.data == "refresh_procs")
async def refresh_processes(callback: types.CallbackQuery):
    try:
        procs = get_top_processes(10)
        text = "📊 Топ 10 процессов по CPU:\n\n"
        builder = InlineKeyboardBuilder()

        for p in procs:
            text += f"`{p['pid']}` - {p['name']} ({p['cpu_percent']}% CPU)\n"
            builder.button(text=f"❌ {p['name']} ({p['pid']})", callback_data=f"kill_{p['pid']}")

        builder.button(text="🔄 Обновить", callback_data="refresh_procs")
        builder.button(text="❌ Закрыть", callback_data="close")
        builder.adjust(1)

        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
    await callback.answer()

@router.callback_query(lambda c: c.data == "close")
async def close_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
