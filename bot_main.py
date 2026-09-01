import asyncio
import logging
import os
import subprocess
import json
import emoji
import re
#import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from fabric import Connection
from dotenv import load_dotenv
from config import PATHS

# Загрузка переменных окружения
load_dotenv(dotenv_path=PATHS['env_file'])

# Настройка логирования
logging.basicConfig(
    filename=PATHS['log_file'],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Загрузка списка разрешенных пользователей из JSON-файла
def load_allowed_users():
    try:
        with open(PATHS['json_file'], "r") as file:
            return tuple(json.load(file))
    except FileNotFoundError:
        logging.error(f"Файл не найден: {PATHS['json_file']}")
        return tuple()
    except json.JSONDecodeError:
        logging.error(f"Ошибка формата JSON в файле: {PATHS['json_file']}")
        return tuple()

ALLOWED_USERS = load_allowed_users()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BRAS_HOSTS = ['10.10.3.40', '10.10.3.45', '10.10.3.100']
APACHE_HOST = '192.168.0.174'
BRAS_USER = "cto"
BRAS_PASSWORD = os.getenv("BRAS_PASSWORD")
APACHE_USER = "tankov"
APACHE_PASSWORD = os.getenv("APACHE_PASSWORD")
ALLOWED_USERS = load_allowed_users()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

def load_allowed_users():
    try:
        with open(PATHS['json_file'], "r") as file:
            return tuple(json.load(file))
    except FileNotFoundError:
        logging.error(f"Файл не найден: {PATHS['json_file']}")
        return tuple()

def normalize_mac(mac: str) -> str:
    """Конвертирует MAC в формат aa:bb:cc:dd:ee:ff"""
    mac_clean = re.sub(r'[^a-fA-F0-9]', '', mac)
    if len(mac_clean) != 12:
        return mac  # Если не MAC, возвращаем оригинал строки
    return ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2)).lower()

async def check_host_and_run_command(host, user, password, command, user_id, success_message, error_message):
    try:
        response = await asyncio.to_thread(subprocess.run, ["ping", "-c", "2", host], capture_output=True, text=True)
        if response.returncode == 0:
            result = Connection(host, user, connect_kwargs={'password': password}).run(command)
            output = result.stdout.strip()
            
            # Проверка на пустой результат
            if not output:
                await bot.send_message(user_id, f"{success_message} | Пустой результат")
            else:
                await bot.send_message(user_id, f"{success_message}\n{output}")
        else:
            await bot.send_message(user_id, error_message)
    except Exception as e:
        await bot.send_message(user_id, f"Ошибка: {e}")

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    if user_id in ALLOWED_USERS:
        await message.reply(f"Привет, {user_full_name}!")
    else:
        await bot.send_message(user_id, "У тебя здесь нет власти!")
    logging.info(f"User {user_id} executed /start command.")

@dp.message(Command('pppoe'))
async def cmd_pppoe(message: types.Message):
    """Обработка команды /pppoe."""
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        await bot.send_message(user_id, "У тебя здесь нет власти!")
        return

    await bot.send_message(user_id, emoji.emojize('5 сек, проверяю... :magnifying_glass_tilted_right:'))

    for host in BRAS_HOSTS:
        await check_host_and_run_command(
            host=host,
            user=BRAS_USER,
            password=BRAS_PASSWORD,
            command='show pppoe summary | i Total',
            user_id=user_id,
            success_message=emoji.emojize(f':index_pointing_at_the_viewer: {host} :x-ray: '),
            error_message=f"Нет подключения к {host}. Проверь маршруты"
        )
    logging.info(f"User {user_id} executed /pppoe command.")

@dp.message(Command('session'))
async def cmd_show_session(message: types.Message, command: CommandObject):
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        await bot.send_message(user_id, "У тебя здесь нет власти!")
        return

    if command.args is None:
        await bot.send_message(user_id, "Введи полный номер договора или MAC-адрес\nПример: /session alt123 или /session aa:bb:cc:dd:ee:ff")
        return

    input_arg = command.args.strip()
    search_arg = normalize_mac(input_arg)  # Пытаемся нормализовать MAC
    
    await bot.send_message(user_id, emoji.emojize('Ищу абонента... :magnifying_glass_tilted_right:'))

    has_results = False  # Флаг наличия результатов
    for host in BRAS_HOSTS:
        try:
            response = await asyncio.to_thread(subprocess.run, ["ping", "-c", "2", host], capture_output=True, text=True)
            if response.returncode == 0:
                result = Connection(host, BRAS_USER, connect_kwargs={'password': BRAS_PASSWORD}).run(f'show pppoe | i {search_arg}')
                output = result.stdout.strip()
                
                if output:
                    has_results = True
                    await bot.send_message(user_id, f"{host}:\n{output}")
#                else:
#                    await bot.send_message(user_id, f"{host} | Совпадений не найдено")
            else:
                await bot.send_message(user_id, f"Нет подключения к {host}. Проверь маршруты")
        except Exception as e:
            await bot.send_message(user_id, f"Ошибка на {host}: {str(e)}")

    # Если ни на одном устройстве не найдено результатов
    if not has_results:
        await bot.send_message(user_id, "Ничего не найдено")

    logging.info(f"User {user_id} executed /session command with args: {input_arg}.")

@dp.message(Command('apache'))
async def cmd_apache(message: types.Message):
    """Обработка команды /apache."""
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        await bot.send_message(user_id, "У тебя здесь нет власти!")
        return

    await bot.send_message(user_id, emoji.emojize('Поднимаем сайт :man_technologist:'))

    await check_host_and_run_command(
        host=APACHE_HOST,
        user=APACHE_USER,
        password=APACHE_PASSWORD,
        command='/usr/local/bin/restartapache2',
        user_id=user_id,
        success_message="Результат: ",
        error_message="Нет подключения к серверу."
    )
    logging.info(f"User {user_id} executed /apache command.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
