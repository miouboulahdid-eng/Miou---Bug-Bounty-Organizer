import os
import time
from datetime import datetime
from config import LOGS_DIR

os.makedirs(LOGS_DIR, exist_ok=True)
MIUO_LOG_FILE = os.path.join(LOGS_DIR, "miou_commands.log")

def log_miou_command(command_line):
    """تسجيل أمر Miou الذي قام به المستخدم."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MIUO_LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] $ {command_line}\n")