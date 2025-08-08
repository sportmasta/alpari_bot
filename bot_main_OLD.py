import asyncio
import time
import logging
import os
import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from fabric import Connection

logging.basicConfig(filename='TGBot.log', level=logging.INFO)

TOKEN = "6440130888:AAEE_QBj0QgBsfCSZx-QtKWaiZYYjyJWyDI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    if user_id == (630071071) or (304882770):
        await message.reply(f"Привет, {user_full_name}!")
    else:
        await bot.send_message(user_id, "У тебя здесь нет власти!")


@dp.message(Command('pppoe'))
async def cmd_pppoe(message: types.Message):
    host = '10.10.3.40'
    user = "cto"
    password = "@Adminno.1"
    user_id = message.from_user.id
    if user_id == (630071071) or (304882770):
        await bot.send_message(user_id, emoji.emojize(f'5 сек, проверяю... :magnifying_glass_tilted_right:'))

        response = os.system("ping -c 2 " + host)
        if response == 0:
            for host in ['10.10.3.40', '10.10.3.45', '10.10.3.100']:
                result = Connection(host, user, connect_kwargs={'password': password}).run('show pppoe summary | i Total')
                await bot.send_message(user_id, emoji.emojize(f':index_pointing_at_the_viewer: '+host+f' :x-ray: {result.stdout}'))                   
        else:
            await bot.send_message(user_id, "Нет подключения к BRAS. Проверь маршруты")
    else:
        await bot.send_message(user_id, "У тебя здесь нет власти!")


@dp.message(Command('session'))
async def cmd_show_session(message: types.Message, command: CommandObject):
    user = "cto"
    password = "@Adminno.1"
    user_id = message.from_user.id
    if user_id == (630071071) or (304882770):
        if command.args is None:
            await bot.send_message(user_id,"Введи полный номер договора\nПример: /session alt123")
            return
        nomerdogovora = command.args
        await bot.send_message(user_id, emoji.emojize(f'Ищу абонента... :magnifying_glass_tilted_right:'))
        response = os.system("ping -c 2 10.10.3.40")
        if response == 0:
            for host in ['10.10.3.40', '10.10.3.45', '10.10.3.100']:
                result = Connection(host, user, connect_kwargs={'password': password}).run(f'show pppoe | i {nomerdogovora}')
                await bot.send_message(user_id, emoji.emojize(f':index_pointing_at_the_viewer: '+host+f' :light_bulb: {result.stdout}'))   
        else:
            await bot.send_message(user_id, "Нет подключения к BRAS. Проверь маршруты")
    else:
        await bot.send_message(user_id, "У тебя здесь нет власти!")

@dp.message(Command('apache'))
async def cmd_pppoe(message: types.Message):
    host = '192.168.0.174'
    user = "tankov"
    password = "@Adminno.1"
    user_id = message.from_user.id
    if user_id == (630071071) or (304882770):
        await bot.send_message(user_id, emoji.emojize(f'Поднимаем сайт :man_technologist:'))

        response = os.system("ping -c 2 " + host)
        if response == 0:
            for host in ['192.168.0.174']:
                result = Connection(host, user, connect_kwargs={'password': password}).run('/usr/local/bin/restartapache2')
                await bot.send_message(user_id, (f'{result.stdout}'))
        else:
            await bot.send_message(user_id, "Нет подключения к серверу.")
    else:
        await bot.send_message(user_id, "У тебя здесь нет власти!")

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
