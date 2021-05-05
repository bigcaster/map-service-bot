# -*- coding: utf-8 -*-
import os
import requests
import telebot
from flask import Flask, request
from data import TOKEN, bot, HEROKU_APP_NAME, format_kind
from markups import main_markup, back_markup, map_type_markup, geo_type_markup, toponym_markup, results_markup, \
    request_markup
from mapAPI import map_api
from getWeather import get_weather

server = Flask(__name__)

PORT = int(os.environ.get('PORT', 5000))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Я бот, работающий с картами и другими инструментами. '
                                      'Получите полное описание по команде "❓ Помощь"',
                     reply_markup=main_markup)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, '''
Команды:

🧭 *Карта*
*Обязательные параметры:*
geocode/геокод: адрес или координаты объекта
kind/топоним: топонима
place/место: название организации
results/результаты: количество результатов
*Дополнительные параметры:*
l/layer/слой: перечень слоев (спутник, схема, гибрид, траффик)
z/zoom/масштаб: уровень масштабирования (0-17)
s/scale/увеличение: коэффициент увеличения объектов (1.0-4.0)

⛅ *Погода* 
Вызовите команду, а затем введите название города

⬅ *Назад*
Возвращает назад
''', parse_mode="Markdown")


@bot.message_handler(commands=["weather"])
def weather(message):
    if message is None:
        return
    bot.send_message(message.chat.id, 'Чтобы узнать погоду, введите название города', reply_markup=back_markup)
    bot.register_next_step_handler(message, get_weather)


@bot.message_handler(commands=['map'])
def map_command(message):
    bot.send_message(message.chat.id, "Выберите тип поиска", reply_markup=map_type_markup)
    bot.register_next_step_handler(message, map_type)


def map_type(message):
    text = message.text.strip().lower()
    if text in ["🗻 поиск по объектам", "поиск по объектам", "объекты"]:
        bot.send_message(message.chat.id, "Введите адрес или координаты", reply_markup=back_markup)
        bot.register_next_step_handler(message, geo)
    elif text in ["🏢 поиск по организациям", "поиск по организациям", "организации"]:
        bot.send_message(message.chat.id, "Введите название организации", reply_markup=back_markup)
        bot.register_next_step_handler(message, place)
    elif text in ["⌨ ввести вручную", "ввести вручную", "вручную"]:
        pass
    elif text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад в главное меню", reply_markup=main_markup)
    else:
        bot.send_message(message.chat.id, "Не удалось распознать тип поиска, попробуйте снова",
                         reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)


def geo(message):
    REQUEST.pop("geocode", None)
    text = message.text.strip().lower()
    if text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска", reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    else:
        REQUEST["geocode"] = text
        bot.send_message(message.chat.id, "Выберите тип поиска по объектам", reply_markup=geo_type_markup)
        bot.register_next_step_handler(message, geo_type)


def geo_type(message):
    text = message.text.strip().lower()
    if text in ["🗻 поиск объектов", "поиск объектов", "объекты"]:
        bot.send_message(message.chat.id, "Задайте количество результатов", reply_markup=results_markup)
        bot.register_next_step_handler(message, results)
    elif text in ["🎪 поиск ближайших топонимов к объекту", "поиск ближайших топонимов к объекту", "топонимы"]:
        bot.send_message(message.chat.id, "Выберите вид топонима", reply_markup=toponym_markup)
        bot.register_next_step_handler(message, toponym)
    elif text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, введите адрес или координаты", reply_markup=back_markup)
        bot.register_next_step_handler(message, geo)
    else:
        bot.send_message(message.chat.id, "Недопустимый тип поиска по объекту, введите снова",
                         reply_markup=geo_type_markup)
        bot.register_next_step_handler(message, geo_type)


def toponym(message):
    REQUEST.pop("kind", None)
    text = message.text.strip().lower()
    if text in ["⬅ назад", "назад"]:
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
    if text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска", reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    else:
        REQUEST["place"] = text
        bot.send_message(message.chat.id, "Задайте количество результатов", reply_markup=results_markup)
        bot.register_next_step_handler(message, results)


def results(message):
    REQUEST.pop("results", None)
    text = message.text.strip().lower()
    if text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, выберите тип поиска",
                         reply_markup=map_type_markup)
        bot.register_next_step_handler(message, map_type)
    elif text.isdigit():
        REQUEST["results"] = text
        bot.send_message(message.chat.id, 'Задайте вручную параметры, которые были установлены по умолчанию. '
                                          'Для этого введите их в формате <параметр>=<значение>, перечисляя с '
                                          'поомощью ";"',
                         reply_markup=request_markup)
        bot.register_next_step_handler(message, make_request)
    else:
        bot.send_message(message.chat.id, "Недопустимое количество результатов, введите снова",
                         reply_markup=results_markup)
        bot.register_next_step_handler(message, results)


def make_request(message):
    global REQUEST
    text = message.text.strip().lower()
    if text in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад, задайте количество результатов",
                         reply_markup=results_markup)
        bot.register_next_step_handler(message, results)
        return
    elif text not in ["➡ пропустить", "пропустить"]:
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
    if text in ['⬅ назад', 'назад']:
        bot.send_message(message.chat.id, "Нет запущенной комманды на данный момент", reply_markup=main_markup)
    elif text in ["🧭 карта", "карта"]:
        map_command(message)
    elif text in ["⛅ погода", "погода"]:
        weather(message)
    elif text in ["❓ помощь", "помощь"]:
        help(message)
    elif text.startswith('/'):
        bot.send_message(message.chat.id, f'Нет команды "{text}"', reply_markup=main_markup)
    else:
        bot.send_message(message.chat.id, "Не удалось обработать запрос", reply_markup=main_markup)


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
