import asyncio
import logging
import os
import subprocess
import json
import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from fabric import Connection
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(filename='TGBot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка списка разрешенных пользователей из JSON-файла
def load_allowed_users():
    try:
        with open("personales.json", "r") as file:
            return tuple(json.load(file))
    except FileNotFoundError:
        logging.error("Файл personales.json не найден.")
        return tuple()
    except json.JSONDecodeError:
        logging.error("Ошибка при чтении personales.json. Убедись, что файл содержит корректный JSON.")
        return tuple()

# Константы
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BRAS_HOSTS = ['10.10.3.40', '10.10.3.45', '10.10.3.100']
APACHE_HOST = '192.168.0.174'
BRAS_USER = "cto"
BRAS_PASSWORD = os.getenv("BRAS_PASSWORD")
APACHE_USER = "tankov"
APACHE_PASSWORD = os.getenv("APACHE_PASSWORD")
ALLOWED_USERS = load_allowed_users()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


async def check_host_and_run_command(host, user, password, command, user_id, success_message, error_message):
    """Проверяет доступность хоста и выполняет команду."""
    try:
        response = await asyncio.to_thread(subprocess.run, ["ping", "-c", "2", host], capture_output=True, text=True)
        if response.returncode == 0:
            result = Connection(host, user, connect_kwargs={'password': password}).run(command)
            await bot.send_message(user_id, success_message + result.stdout)
        else:
            await bot.send_message(user_id, error_message)
    except Exception as e:
        await bot.send_message(user_id, f"Ошибка: {e}")


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    """Обработка команды /start."""
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
    """Обработка команды /session."""
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        await bot.send_message(user_id, "У тебя здесь нет власти!")
        return

    if command.args is None:
        await bot.send_message(user_id, "Введи полный номер договора\nПример: /session alt123")
        return

    nomerdogovora = command.args
    await bot.send_message(user_id, emoji.emojize('Ищу абонента... :magnifying_glass_tilted_right:'))

    for host in BRAS_HOSTS:
        await check_host_and_run_command(
            host=host,
            user=BRAS_USER,
            password=BRAS_PASSWORD,
            command=f'show pppoe | i {nomerdogovora}',
            user_id=user_id,
            success_message=emoji.emojize(f':index_pointing_at_the_viewer: {host} :light_bulb: '),
            error_message=f"Нет подключения к {host}. Проверь маршруты"
        )
    logging.info(f"User {user_id} executed /session command with args: {nomerdogovora}.")


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
    """Запуск бота."""
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())