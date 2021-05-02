# -*- coding: utf-8 -*-
from datetime import datetime

import requests
import telebot
from pycbrf import ExchangeRates
from mapAPI import MapAPI
import os
from flask import Flask, request
from data import format_kind

server = Flask(__name__)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = "1719349692:AAHNGDF0WeCkGXy3Ef8uWuYXtWmzQF4VypE"
HEROKU_APP_NAME = "map-service-bot"
url = 'http://api.openweathermap.org/data/2.5/weather'
api_weather = 'e4a3da131fe7dd1aa4d06d1ded5c6963'
bot = telebot.TeleBot(TOKEN)
map_api = MapAPI()

main_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main1 = telebot.types.KeyboardButton("🧭Карта")
main2 = telebot.types.KeyboardButton("⛅Погода")
main3 = telebot.types.KeyboardButton("💸Валюты")
main4 = telebot.types.KeyboardButton("❓Помощь")

main_markup.row(main1, main2, main3, main4)
back_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
back = telebot.types.KeyboardButton('⬅Назад')
back_markup.add(back)
currency_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

currency1 = telebot.types.KeyboardButton("💷GBP")
currency2 = telebot.types.KeyboardButton("💶EUR")
currency3 = telebot.types.KeyboardButton("💴CNY")
currency4 = telebot.types.KeyboardButton("💵USD")
currency_markup.row(currency1, currency2, currency3, currency4)
currency_markup.add(back)

map_type_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
type1 = telebot.types.KeyboardButton("🗻Поиск по объектам")
type2 = telebot.types.KeyboardButton("🏢Поиск по организациям")
map_type_markup.row(type1, type2)
map_type_markup.add(back)

geo_type_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
geo1 = telebot.types.KeyboardButton("🗻Поиск объектов")
geo2 = telebot.types.KeyboardButton("🎪Поиск ближайших топонимов к объекту")
geo_type_markup.row(geo1, geo2)
geo_type_markup.add(back)

toponym_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
toponym1 = telebot.types.KeyboardButton("🏠Дом")
toponym2 = telebot.types.KeyboardButton("🛣Улица")
toponym3 = telebot.types.KeyboardButton("🚇Метро")
toponym4 = telebot.types.KeyboardButton("🏙Район")
toponym5 = telebot.types.KeyboardButton("🏘Населенный пункт")
toponym_markup.row(toponym1, toponym2, toponym3)
toponym_markup.row(toponym4, toponym5)
toponym_markup.add(back)

results_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
results1 = telebot.types.KeyboardButton("1")
results2 = telebot.types.KeyboardButton("3")
results3 = telebot.types.KeyboardButton("5")
results_markup.add(results1, results2, results3, back)

request_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
request1 = telebot.types.KeyboardButton("➡Пропустить")
request_markup.add(request1, back)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Я бот, умеющий работать с картами и другими инструментами.'
                                      'Для получения полной информации, введите "Помощь"', reply_markup=main_markup)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, '''Этот бот в основном специализируется на работе с картами.
Параметры:
layer/слой: перечень слоев, (спутник, схема, гибрид, траффик)
zoom/масштаб: масштаб изображения (от 0 до 17)
scale/увеличение: коэффициент увеличения объектов на карте (от 1.0 до 4.0)
Другие команды:
⛅Погода: вывод погоды по городу
💸Валюты: курс валют (GBP, EUR, CNY, USD)
⬅Назад: вернуться назад.''')


@bot.message_handler(commands=["weather"])
def weather(message):
    if message is None:
        return
    bot.send_message(message.chat.id, 'Чтобы узнать погоду, введите название города', reply_markup=back_markup)
    bot.register_next_step_handler(message, get_weather)


def get_weather(message):
    city_name = message.text.strip().lower()
    if city_name in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Возвращаемся назад", reply_markup=main_markup)
        return
    try:
        params = {'APPID': api_weather, 'q': city_name, 'units': 'metric', 'lang': 'ru'}
        result = requests.get(url, params=params)
        weather = result.json()
        deg = weather['wind']['deg']
        wind_direction = [("С", abs(0 - deg)), ("В", abs(90 - deg)), ("Ю", abs(180 - deg)), ("З", abs(270 - deg))]
        wind_direction.sort(key=lambda s: s[1])
        bot.send_message(message.chat.id,
                         f"Погода в городе {str(weather['name'])}:\n"
                         f"температура: {str(int(weather['main']['temp']))}°\n"
                         f"Ощущается как: {str(int(weather['main']['feels_like']))}°\n"
                         f"Скорость ветра: {str(float(weather['wind']['speed']))} м/с, {wind_direction[0][0]}\n"
                         f"Давление: {str(float(weather['main']['pressure']))} мм рт. ст.\n"
                         f"Влажность: {str(int(weather['main']['humidity']))}%\n"
                         f"Видимость: {str(weather['visibility'])}\n"
                         f"Описание: {str(weather['weather'][0]['description'])}\n", reply_markup=main_markup)
    except Exception:
        bot.send_message(message.chat.id, "Город " + city_name + " не найден", reply_markup=main_markup)


@bot.message_handler(commands=["currency"])
def currency(message):
    bot.send_message(chat_id=message.chat.id, text="Какой курс валюты вас интересует?",
                     reply_markup=currency_markup, parse_mode="html")
    bot.register_next_step_handler(message, exchange_rate)


def exchange_rate(message):
    text = message.text.strip().lower()
    if text in ['⬅назад', 'назад']:
        bot.send_message(message.chat.id, "Возвращаемся назад", reply_markup=main_markup)
    else:
        if text in ['💵usd', '💶eur', '💴cny', '💷gbp']:
            text = text[1:]
        if text in ['usd', 'eur', 'cny', 'gbp']:
            rates = ExchangeRates(datetime.now())
            bot.send_message(chat_id=message.chat.id,
                             text=f"<b>Сейчас курс: {text.upper()} = {float(rates[text.upper()].rate)}</b>",
                             parse_mode="html", reply_markup=main_markup)
        else:
            bot.send_message(message.chat.id, f'Не надйен курс валюты: {text.upper()}', reply_markup=main_markup)


@bot.message_handler(commands=['map'])
def map_command(message):
    bot.send_message(message.chat.id, "Выберите тип поиска", reply_markup=map_type_markup)
    bot.register_next_step_handler(message, map_type)


def map_type(message):
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад в главное меню", reply_markup=main_markup)
    elif text in ["🗻поиск по объектам", "поиск по объектам", "объекты"]:
        bot.send_message(message.chat.id, "Введите адрес или координаты", reply_markup=back_markup)
        bot.register_next_step_handler(message, geo)
    elif text in ["🏢поиск по организациям", "поиск по организациям", "организации"]:
        bot.send_message(message.chat.id, "Введите название организации", reply_markup=back_markup)
        bot.register_next_step_handler(message, place)
    else:
        bot.send_message(message.chat.id, "Не удалось распознать тип поиска, попробуйте снова",
                         reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)


def geo(message):
    REQUEST.pop("geocode", None)
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад. Выберите тип поиска", reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    else:
        REQUEST["geocode"] = text
        bot.send_message(message.chat.id, "Выберите тип поиска по объектам", reply_markup=geo_type_markup)
        bot.register_next_step_handler(message, geo_type)


def geo_type(message):
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, введите адрес или координаты", reply_markup=back_markup)
        bot.register_next_step_handler(message, geo)
    elif text in ["🗻поиск объектов", "поиск объектов", "объекты"]:
        bot.send_message(message.chat.id, "Задайте количество результатов", reply_markup=results_markup)
        bot.register_next_step_handler(message, results)
    elif text in ["🎪поиск ближайших топонимов к объекту", "поиск ближайших топонимов к объекту", "топонимы"]:
        bot.send_message(message.chat.id, "Выберите вид топонима", reply_markup=toponym_markup)
        bot.register_next_step_handler(message, toponym)
    else:
        bot.send_message(message.chat.id, "Недопустимый тип поиска по объекту, введите снова",
                         reply_markup=geo_type_markup)
        bot.register_next_step_handler(message, geo_type)


def toponym(message):
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска по объектам",
                         reply_markup=geo_type_markup)
        bot.register_next_step_handler(message, geo_type)
    elif text in format_kind:
        REQUEST["kind"] = format_kind[text]
        bot.send_message(message.chat.id, "Задайте количество результатов", reply_markup=results_markup)
        bot.register_next_step_handler(message, results)
    else:
        bot.send_message(message.chat.id, "Недопустимый вид топонима, введите снова", reply_markup=toponym_markup)
        bot.register_next_step_handler(message, toponym)


def place(message):
    REQUEST.pop("place", None)
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска", reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    else:
        REQUEST["place"] = text
        bot.send_message(message.chat.id, "Задайте количество результатов", reply_markup=results_markup)
        bot.register_next_step_handler(message, results)


def results(message):
    REQUEST.pop("results", None)
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска",
                         reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    elif text.isdigit():
        REQUEST["results"] = text
        bot.send_message(message.chat.id, 'Задайте вручную параметры по умолчанию. Для этого введите их по в формате '
                                          '<параметр>=<значение>, перечисляя с поомощью ";"',
                         reply_markup=request_markup)
        bot.register_next_step_handler(message, make_request)
    else:
        bot.send_message(message.chat.id, "Недопустимое количество результатов, введите снова",
                         reply_markup=results_markup)
        bot.register_next_step_handler(message, results)


def make_request(message):
    global REQUEST
    text = message.text.strip().lower()
    if text in ["⬅назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, задайте количество результатов",
                         reply_markup=results_markup)
        bot.register_next_step_handler(message, results)
        return
    elif text not in ["➡пропустить", "пропустить"]:
        REQUEST.update({param.split("=")[0]: param.split("=")[1] for param in text.split(';')})
    output = map_api.main(";".join([f"{key}={value}" for key, value in REQUEST.items()]))
    if isinstance(output, str):
        bot.send_message(message.chat.id, output, reply_markup=main_markup)
    else:
        im = open("map.png", "rb")
        description = []
        for d in output:
            raw = []
            for key, value in d.items():
                if key != 'spn':
                    raw.append(f"{key}: {value}")
            description.append('\n'.join(raw))
        description.insert(0, f'По вашему запросу найдено результатов: {len(description)}:')
        description = '\n\n'.join(description)
        if len(description) > 963:
            description = description[:963] + "...\n...описание слишком длинное, что отобразить его полностью"
        bot.send_photo(message.chat.id, im, caption=description, reply_markup=main_markup)
    REQUEST = {}


@bot.message_handler(content_types=["text"])
def dialog(message):
    text = message.text.strip().lower()
    if text in ["🧭карта", "карта"]:
        map_command(message)
    elif text in ["⛅погода", "погода"]:
        weather(message)
    elif text in ["💸валюты", "валюты"]:
        currency(message)
    elif text in ["❓помощь", "помощь"]:
        help(message)
    elif text.startswith('/'):
        bot.send_message(message.chat.id, f'Нет команды "{text}"', reply_markup=main_markup)
    elif text in ['⬅назад', 'назад']:
        bot.send_message(message.chat.id, "Нет запущенной комманды на данный момент", reply_markup=main_markup)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
    return "?", 200


if __name__ == '__main__':
    REQUEST = {}
    server.run(host="0.0.0.0", port=PORT)
