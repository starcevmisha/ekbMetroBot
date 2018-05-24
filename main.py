import bisect
import datetime
import os

import requests
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from schedule import workday_times, weekend_times

if "HEROKU" in os.environ:
    token = os.environ.get('TOKEN')
else:
    from secret import token

server = Flask(__name__)
bot = telebot.TeleBot(token)


@server.route("/", methods=['POST'])
def get_message():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/')
def hello_world():
    return 'Hello! Try get my telegram bot @EkbMetroBot'


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    choose_station(message)


stations = {'Космонавтов', 'Уралмаш на Космонавтов', 'Уралмаш на Ботанику', 'Машиностроителей на Космонавтов',
            'Машиностроителей на Ботанику', 'Уральская на Космонавтов', 'Уральская на Ботанику',
            'Динамо на Космонавтов',
            'Динамо на Ботанику', 'Площадь 1905 года на Космонавтов', 'Площадь 1905 года на Ботанику',
            'Геологическая на Космонавтов', 'Геологическая на Ботанику', 'Чкаловская на Космонавтов',
            'Чкаловская на Ботанику',
            'Ботанническая'}


@bot.message_handler(func=lambda message: message.text in stations,
                     content_types=["text"])
def send_time(message):
    date = datetime.date.today().strftime('%Y%m%d')
    time = datetime.datetime.now().strftime("%H:%M")
    if requests.get(f"https://isdayoff.ru/{date}").text == 1:
        index = bisect.bisect_left(weekend_times[message.text], time)
        left = 0 if index == 0 else index - 1
        right = len(weekend_times[message.text]) - 1 if index == len(weekend_times[message.text]) else index + 2
        result = weekend_times[message.text][left:right]
    else:
        index = bisect.bisect_left(workday_times[message.text], time)
        left = 0 if index == 0 else index - 1
        right = len(workday_times[message.text]) - 1 if index == len(workday_times[message.text]) else index + 2
        result = workday_times[message.text][left:right]
    bot.send_message(message.chat.id, f"Your time{time}\n" + ' '.join(result), reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def choose_station(message):
    bot.send_message(message.chat.id, "Выбери остановку", reply_markup=keyboard)




keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard.add("Космонавтов")
keyboard.add(KeyboardButton("Уралмаш на Космонавтов"), KeyboardButton("Уралмаш на Ботанику"))
keyboard.add(KeyboardButton("Машиностроителей на Космонавтов"), KeyboardButton("Машиностроителей на Ботанику"))
keyboard.add(KeyboardButton("Уральская на Космонавтов"), KeyboardButton("Уральская на Ботанику"))
keyboard.add(KeyboardButton("Динамо на Космонавтов"), KeyboardButton("Динамо на Ботанику"))
keyboard.add(KeyboardButton("Площадь 1905 года на Космонавтов"), KeyboardButton("Площадь 1905 года на Ботанику"))
keyboard.add(KeyboardButton("Геологическая на Космонавтов"), KeyboardButton("Геологическая на Ботанику"))
keyboard.add(KeyboardButton("Чкаловская на Космонавтов"), KeyboardButton("Чкаловская на Ботанику"))
keyboard.add("Ботанническая")

if __name__ == '__main__':
    if "HEROKU" in os.environ:
        PORT = int(os.environ.get('PORT', '5000'))
        server.run("0.0.0.0", PORT)
    else:
        bot.set_webhook("https://5d96028a.ngrok.io")
        server.run("127.0.0.1", 9090)
