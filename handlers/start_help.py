# handlers/start_help.py
from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import is_user_allowed, is_admin, add_user
from utils.system_monitor import get_system_status

router = Router()

@router.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    # Проверяем, является ли пользователь админом из .env
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            admin_id_from_env = int(env_content.split('ADMIN_ID=')[1].split('\n')[0])
            if user_id == admin_id_from_env:
                add_user(user_id, is_admin=True)
    except:
        pass  # Если не удалось прочитать .env, продолжаем как обычно
    
    if not is_user_allowed(user_id):
        await message.answer("👋 Привет! У вас нет доступа к этому боту.")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статус", callback_data="show_status")
    builder.button(text="📋 Помощь", callback_data="show_help")
    if is_admin(user_id):
        builder.button(text="⚙️ Админ панель", callback_data="admin_panel")
    builder.adjust(2)
    
    welcome_text = f"👋 Добро пожаловать, {username}!\n\n"
    welcome_text += "Я бот для управления вашим VDS сервером.\n"
    welcome_text += "Используйте кнопки ниже или команды для управления сервером."
    
    await message.answer(welcome_text, reply_markup=builder.as_markup())

@router.message(lambda message: message.text == "/help")
async def help_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not is_user_allowed(user_id):
        await message.answer("❌ У вас нет доступа к этому боту.")
        return
    
    is_user_admin = is_admin(user_id)
    
    help_text = "🤖 *Команды бота:*\n\n"
    help_text += "🔍 *Мониторинг:*\n"
    help_text += "`/status` - Статус сервера\n"
    help_text += "`/logs [N]` - Последние N строк логов\n"
    help_text += "`/processes` - Список процессов\n"
    help_text += "`/ports` - Открытые порты\n"
    help_text += "`/connections` - Активные соединения\n\n"
    
    help_text += "サービс *Сервисы:*\n"
    help_text += "`/services` - Список сервисов\n"
    help_text += "`/restart [сервис]` - Перезапуск сервиса\n"
    help_text += "`/start [сервис]` - Запуск сервиса\n"
    help_text += "`/stop [сервис]` - Остановка сервиса\n\n"
    
# handlers/start_help.py (фрагмент в help_handler)
    if is_user_admin:
        help_text += "🔐 *Админ команды:*\n"
        help_text += "`/auth [user_id]` - Добавить пользователя\n"
        help_text += "`/exec [команда]` - Выполнить shell команду\n"
        help_text += "`/backup` - Управление бэкапами\n"
        help_text += "`/adduser <username> [pass]` - Создать пользователя\n" # Новая команда
        help_text += "`/deluser <username>` - Удалить пользователя\n"       # Новая команда
        help_text += "\n"
    help_text += "ℹ️ *Дополнительно:*\n"
    help_text += "`/start` - Начать работу\n"
    help_text += "`/help` - Показать помощь"
    
    await message.answer(help_text, parse_mode="Markdown")

# Callback handlers для кнопок
@router.callback_query(lambda c: c.data == "show_status")
async def show_status_callback(callback: types.CallbackQuery):
    status = get_system_status()
    response = (
        f"💻 *Статус сервера:*\n"
        f"🔹 CPU: {status['cpu']}%\n"
        f"🔹 RAM: {status['memory']}\n"
        f"🔹 Диск: {status['disk']}\n"
        f"🔹 Аптайм: {status['uptime']}\n"
        f"🔹 IP: `{status['ip']}`"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="back_to_main")
    builder.adjust(1)
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data == "show_help")
async def show_help_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_user_admin = is_admin(user_id)
    
    help_text = "🤖 *Команды бота:*\n\n"
    help_text += "🔍 *Мониторинг:*\n"
    help_text += "`/status` - Статус сервера\n"
    help_text += "`/logs [N]` - Последние N строк логов\n"
    help_text += "`/processes` - Список процессов\n"
    help_text += "`/ports` - Открытые порты\n"
    help_text += "`/connections` - Активные соединения\n\n"
    
    help_text += "サービс *Сервисы:*\n"
    help_text += "`/services` - Список сервисов\n"
    help_text += "`/restart [сервис]` - Перезапуск сервиса\n"
    help_text += "`/start [сервис]` - Запуск сервиса\n"
    help_text += "`/stop [сервис]` - Остановка сервиса\n\n"
    
    if is_user_admin:
        help_text += "🔐 *Админ команды:*\n"
        help_text += "`/auth [user_id]` - Добавить пользователя\n"
        help_text += "`/exec [команда]` - Выполнить shell команду\n"
        help_text += "`/backup` - Управление бэкапами\n\n"
    
    help_text += "ℹ️ *Дополнительно:*\n"
    help_text += "`/start` - Начать работу\n"
    help_text += "`/help` - Показать помощь"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="back_to_main")
    builder.adjust(1)
    
    await callback.message.edit_text(help_text, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💾 Создать бэкап", callback_data="create_backup")
    builder.button(text="📋 Список бэкапов", callback_data="list_backups")
    builder.button(text="⬅️ Назад", callback_data="back_to_main")
    builder.button(text="❌ Закрыть", callback_data="close_backup")
    builder.adjust(2)
    
    await callback.message.edit_text("🔧 Управление бэкапами:", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статус", callback_data="show_status")
    builder.button(text="📋 Помощь", callback_data="show_help")
    if is_admin(user_id):
        builder.button(text="⚙️ Админ панель", callback_data="admin_panel")
    builder.adjust(2)
    
    welcome_text = "👋 Главное меню\n\nВыберите действие:"
    
    await callback.message.edit_text(welcome_text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data == "close_backup")
async def close_backup_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
