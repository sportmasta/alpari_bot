import os
import sys

# Автоматическое определение режима
IS_COMPILED = getattr(sys, 'frozen', False)

# Базовые пути
BASE_DIR = "/opt/telegramBot/telegramBot" if not IS_COMPILED else os.path.dirname(sys.executable)

# Пути к файлам
PATHS = {
    'env_file': os.path.join(BASE_DIR, ".env"),
    'json_file': os.path.join(BASE_DIR, "personales.json"),
    'log_file': os.path.join(BASE_DIR, "TGBot.log")
}