# handlers/backup.py
import asyncio
import logging
import os
from aiogram import Router, types
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.config import EMAIL_CONFIG, YANDEX_DISK_TOKEN
from utils.backup import create_backup, list_backups, send_backup_via_email
from utils.security import is_admin

router = Router()
logger = logging.getLogger(__name__)

# Константа для максимального размера файла для отправки в Telegram
TELEGRAM_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

@router.message(lambda message: message.text == "/backup")
async def backup_handler(message: types.Message):
    """Обработчик команды /backup - показывает меню управления бэкапами."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только администратор может создавать бэкапы.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="💾 Создать бэкап", callback_data="create_backup")
    builder.button(text="📋 Список бэкапов", callback_data="list_backups")
    builder.button(text="⬅️ Назад", callback_data="back_to_main")
    builder.button(text="❌ Закрыть", callback_data="close_backup")
    builder.adjust(2)

    await message.answer("🔧 Управление бэкапами:", reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data == "create_backup")
async def create_backup_callback(callback: types.CallbackQuery):
    """
    Обработчик callback-запроса для создания бэкапа.
    Отвечает сразу, чтобы избежать таймаута, затем запускает фоновую задачу.
    """
    await callback.answer("⏳ Создаю бэкап...", show_alert=False)
    
    # Запускаем создание бэкапа в фоновой задаче, чтобы не блокировать callback
    asyncio.create_task(_create_backup_background_task(callback))

async def _create_backup_background_task(callback: types.CallbackQuery):
    """
    Фоновая задача для создания бэкапа и его отправки.
    Выполняется асинхронно.
    """
    try:
        # 1. Создаем бэкап
        backup_path, error = create_backup()
        
        if error:
            await callback.message.edit_text(f"❌ Ошибка создания бэкапа: {error}")
            return
        
        if not backup_path or not os.path.exists(backup_path):
            await callback.message.edit_text("❌ Не удалось создать бэкап: файл не найден.")
            return

        # 2. Получаем информацию о файле
        filename = os.path.basename(backup_path)
        size = os.path.getsize(backup_path)
        size_mb = round(size / (1024 * 1024), 2)
        logger.info(f"Бэкап создан: {filename}, размер: {size_mb} MB")

        # 3. Формируем начальное сообщение
        response_text = f"✅ Бэкап создан!\n📁 Файл: `{filename}`\n📊 Размер: {size_mb} MB"

        # 4. Определяем способ доставки и отправляем
        if size <= TELEGRAM_MAX_FILE_SIZE:
            # Отправляем в Telegram
            success, msg = await _send_to_telegram(callback, backup_path, filename, size_mb)
        else:
            # Отправляем на почту
            success, msg = await _send_to_email(backup_path, filename, size_mb)
        
        # 5. Обновляем сообщение с результатом доставки
        response_text += f"\n{msg}"
        
        # 6. Обновляем исходное сообщение с кнопками
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Назад", callback_data="admin_panel")
        builder.button(text="❌ Закрыть", callback_data="close_backup")
        builder.adjust(1)
        
        await callback.message.edit_text(response_text, parse_mode="Markdown", reply_markup=builder.as_markup())
        
    except Exception as e:
        logger.error(f"Ошибка в _create_backup_background_task: {e}", exc_info=True)
        try:
            await callback.message.edit_text(f"❌ Критическая ошибка: {str(e)}")
        except:
            # Если не удалось обновить сообщение, логируем и выходим
            logger.error("Не удалось обновить сообщение после критической ошибки.")

async def _send_to_telegram(callback: types.CallbackQuery, file_path: str, filename: str, size_mb: float) -> tuple[bool, str]:
    """
    Отправляет файл бэкапа в Telegram.
    Возвращает кортеж (успех: bool, сообщение: str).
    """
    try:
        with open(file_path, 'rb') as file:
            input_file = BufferedInputFile(file.read(), filename=filename)
            await callback.message.bot.send_document(
                chat_id=callback.message.chat.id,
                document=input_file,
                caption=f"📄 Бэкап создан: `{filename}`\n📦 Размер: {size_mb} MB",
                parse_mode="Markdown"
            )
        logger.info(f"Бэкап {filename} успешно отправлен в Telegram.")
        return True, "📤 Отправлен в Telegram."
    except Exception as e:
        logger.error(f"Ошибка отправки файла в Telegram: {e}")
        return False, f"⚠️ Не удалось отправить в Telegram: {e}"


async def _send_to_email(file_path: str, filename: str, size_mb: float) -> tuple[bool, str]:
    """Отправляет файл бэкапа на почту или ссылку на него."""
    from utils.backup import upload_to_yandex_disk, send_backup_link_via_email # Импортируем новые функции

    if not EMAIL_CONFIG:
        msg = "⚠️ Файл > 20MB, но почта не настроена."
        logger.warning(msg)
        return False, msg

    recipient_email = EMAIL_CONFIG['sender_email']
    
    # Попробуем сначала загрузить на Яндекс.Диск
    if YANDEX_DISK_TOKEN:
        logger.info("Попытка загрузки бэкапа на Яндекс.Диск...")
        success, result_or_error = upload_to_yandex_disk(file_path, YANDEX_DISK_TOKEN)
        if success:
            logger.info(f"Бэкап загружен на Яндекс.Диск: {result_or_error}")
            # Отправляем ссылку по почте
            link_success, link_msg = send_backup_link_via_email(file_path, recipient_email, result_or_error)
            if link_success:
                return True, "📤 Ссылка на бэкап отправлена на почту (Яндекс.Диск)."
            else:
                return False, f"⚠️ Бэкап загружен, но ошибка отправки ссылки: {link_msg}"
        else:
            logger.error(f"Ошибка загрузки на Яндекс.Диск: {result_or_error}")
            return False, f"⚠️ Ошибка загрузки на Яндекс.Диск: {result_or_error}"
    else:
        # Если Яндекс.Диск не настроен, просто сообщаем, что файл слишком большой
        msg = "⚠️ Файл > 20MB и Яндекс.Диск не настроен. Файл сохранен локально."
        logger.warning(msg)
        return False, msg

@router.callback_query(lambda c: c.data == "list_backups")
async def list_backups_callback(callback: types.CallbackQuery):
    """Обработчик callback-запроса для отображения списка бэкапов."""
    backups, error = list_backups()
    
    if error:
        await callback.message.edit_text(f"❌ Ошибка получения списка бэкапов: {error}")
        await callback.answer()
        return
    
    if not backups:
        response = "📭 Нет доступных бэкапов."
    else:
        response = "📋 Список бэкапов:\n\n"
        # Показываем последние 10 бэкапов
        for backup in backups[-10:]:
            try:
                size_mb = round(backup['size'] / (1024 * 1024), 2)
                date_str = backup['date'].strftime("%Y-%m-%d %H:%M")
                response += f"• `{backup['name']}`\n  📅 {date_str} | 📊 {size_mb} MB\n\n"
            except Exception as e:
                logger.warning(f"Ошибка форматирования бэкапа {backup.get('name', 'Unknown')}: {e}")
                response += f"• `{backup.get('name', 'Unknown')}`\n  (ошибка получения информации)\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="admin_panel")
    builder.button(text="❌ Закрыть", callback_data="close_backup")
    builder.adjust(1)
    
    await callback.message.edit_text(response, parse_mode="MarkdownV2", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(lambda c: c.data == "close_backup")
async def close_backup_callback(callback: types.CallbackQuery):
    """Обработчик callback-запроса для закрытия меню бэкапов."""
    await callback.message.delete()
    await callback.answer()

@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_redirect(callback: types.CallbackQuery):
    """Обработчик callback-запроса для возврата в админ-панель."""
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
