# handlers/network.py
from aiogram import Router, types
from utils.security import is_user_allowed
import subprocess
import os

router = Router()

@router.message(lambda message: message.text == "/ports")
async def list_ports(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    try:
        # Проверяем наличие ss
        try:
            output = subprocess.check_output(["ss", "-tuln"], text=True)
            lines = output.splitlines()
            
            if len(lines) <= 1:
                await message.answer("📭 Нет открытых портов.")
                return

            response = "🔓 Открытые порты:\n```\n"
            response += f"{'PROTO':<8} {'LOCAL ADDRESS':<25} {'STATE':<15}\n"
            response += "-" * 50 + "\n"
            
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0]
                    local_addr = parts[4] if len(parts) > 4 else "N/A"
                    state = parts[1] if len(parts) > 1 else "UNKNOWN"
                    response += f"{proto:<8} {local_addr:<25} {state:<15}\n"
            
            response += "```"
            await message.answer(response, parse_mode="MarkdownV2")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Если ss недоступен, пробуем netstat
        
        # Проверяем наличие netstat
        try:
            output = subprocess.check_output(["netstat", "-tuln"], text=True)
            lines = output.splitlines()
            
            if len(lines) <= 1:
                await message.answer("📭 Нет открытых портов.")
                return

            response = "🔓 Открытые порты:\n```\n"
            response += f"{'Proto':<8} {'Local Address':<25} {'State':<15}\n"
            response += "-" * 50 + "\n"
            
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 4:
                    proto = parts[0]
                    local_addr = parts[3] if len(parts) > 3 else "N/A"
                    state = parts[5] if len(parts) > 5 else "UNKNOWN"
                    response += f"{proto:<8} {local_addr:<25} {state:<15}\n"
            
            response += "```"
            await message.answer(response, parse_mode="MarkdownV2")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Если netstat недоступен, пробуем lsof
        
        # Проверяем наличие lsof
        try:
            output = subprocess.check_output(["lsof", "-i", "-P", "-n"], text=True)
            lines = output.splitlines()
            
            if len(lines) <= 1:
                await message.answer("📭 Нет открытых портов.")
                return

            response = "🔓 Открытые порты:\n```\n"
            response += f"{'COMMAND':<10} {'PID':<8} {'USER':<8} {'FD':<4} {'TYPE':<6} {'DEVICE':<10} {'SIZE/OFF':<12} {'NODE':<8} {'NAME':<20}\n"
            response += "-" * 100 + "\n"
            
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 9:
                    command = parts[0]
                    pid = parts[1]
                    user = parts[2]
                    fd = parts[3]
                    type_ = parts[4]
                    device = parts[5]
                    size_off = parts[6]
                    node = parts[7]
                    name = parts[8]
                    
                    # Извлекаем порт из имени
                    port = ""
                    if ":" in name:
                        port = name.split(":")[-1]
                    
                    response += f"{command:<10} {pid:<8} {user:<8} {fd:<4} {type_:<6} {device:<10} {size_off:<12} {node:<8} {name:<20}\n"
            
            response += "```"
            await message.answer(response, parse_mode="MarkdownV2")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Если lsof недоступен, выдаем ошибку
        
        # Если ничего не работает
        await message.answer("❌ Не удалось получить информацию о портах. Убедитесь, что установлены ss, netstat или lsof.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.message(lambda message: message.text == "/connections")
async def list_connections(message: types.Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Доступ запрещён.")
        return

    try:
        # Проверяем наличие ss
        try:
            output = subprocess.check_output(["ss", "-tuln"], text=True)
            lines = output.splitlines()
            
            if len(lines) <= 1:
                await message.answer("📭 Нет активных соединений.")
                return

            response = "🔗 Активные соединения:\n```\n"
            response += f"{'PROTO':<6} {'LOCAL ADDR':<20} {'PEER ADDR':<20} {'STATE':<15}\n"
            response += "-" * 70 + "\n"
            
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0]
                    local_addr = parts[4] if len(parts) > 4 else "N/A"
                    peer_addr = parts[5] if len(parts) > 5 else "N/A"
                    state = parts[1] if len(parts) > 1 else "UNKNOWN"
                    response += f"{proto:<6} {local_addr:<20} {peer_addr:<20} {state:<15}\n"
            
            response += "```"
            await message.answer(response, parse_mode="MarkdownV2")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Если ss недоступен, пробуем netstat
        
        # Проверяем наличие netstat
        try:
            output = subprocess.check_output(["netstat", "-tuln"], text=True)
            lines = output.splitlines()
            
            if len(lines) <= 1:
                await message.answer("📭 Нет активных соединений.")
                return

            response = "🔗 Активные соединения:\n```\n"
            response += f"{'Proto':<6} {'Local Address':<20} {'Peer Address':<20} {'State':<15}\n"
            response += "-" * 70 + "\n"
            
            for line in lines[1:]:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 4:
                    proto = parts[0]
                    local_addr = parts[3] if len(parts) > 3 else "N/A"
                    peer_addr = parts[4] if len(parts) > 4 else "N/A"
                    state = parts[5] if len(parts) > 5 else "UNKNOWN"
                    response += f"{proto:<6} {local_addr:<20} {peer_addr:<20} {state:<15}\n"
            
            response += "```"
            await message.answer(response, parse_mode="MarkdownV2")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Если netstat недоступен, выдаем ошибку
        
        # Если ничего не работает
        await message.answer("❌ Не удалось получить информацию о соединениях. Убедитесь, что установлены ss или netstat.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
