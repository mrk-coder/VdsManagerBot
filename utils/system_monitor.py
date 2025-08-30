# utils/system_monitor.py (альтернативная версия)
import psutil
import subprocess
import os

def get_system_status():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = subprocess.check_output(["uptime", "-p"], text=True).strip()
    try:
        ip = subprocess.check_output("hostname -I", shell=True, text=True).strip()
    except:
        ip = "Не удалось получить IP"
    return {
        "cpu": cpu,
        "memory": f"{mem.percent}%",
        "disk": f"{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB",
        "uptime": uptime,
        "ip": ip
    }

def get_logs(lines: int = 50):
    """Получает логи с обработкой ошибок"""
    try:
        # Пробуем получить логи через journalctl (предпочтительный способ)
        output = subprocess.check_output(
            ["journalctl", "--since", "1 hour ago", "-n", str(lines), "-q"], 
            text=True, 
            stderr=subprocess.DEVNULL
        )
        return output
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Если journalctl недоступен, пробуем другие способы
        log_files = [
            "/var/log/syslog",
            "/var/log/messages"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file) and os.access(log_file, os.R_OK):
                try:
                    output = subprocess.check_output(
                        ["tail", "-n", str(lines), log_file], 
                        text=True, 
                        stderr=subprocess.DEVNULL
                    )
                    return output
                except:
                    continue
        
        # Если ничего не работает, возвращаем сообщение об ошибке
        return "❌ Не удалось получить логи. Убедитесь, что бот запущен с правами доступа к лог-файлам или установлен journalctl."

def get_top_processes(n=10):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:n]

def kill_process(pid: int):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=3)
        return True, "Процесс успешно завершен"
    except psutil.NoSuchProcess:
        return False, "Процесс не найден"
    except psutil.TimeoutExpired:
        proc.kill()
        return True, "Процесс убит принудительно"
    except Exception as e:
        return False, f"Ошибка: {e}"
