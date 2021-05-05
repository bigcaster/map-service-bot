import requests
from data import url, api_weather, bot
from markups import main_markup


def get_weather(message):
    city_name = message.text.strip().lower()
    if city_name in ["⬅ назад", "назад"]:
        bot.send_message(message.chat.id, "Вернулись назад", reply_markup=main_markup)
        return
    try:
        params = {'APPID': api_weather, 'q': city_name, 'units': 'metric', 'lang': 'ru'}
        result = requests.get(url, params=params)
        weather = result.json()
        deg = weather['wind']['deg']
        wind_direction = [("С", abs(0 - deg)), ("В", abs(90 - deg)), ("Ю", abs(180 - deg)), ("З", abs(270 - deg))]
        wind_direction.sort(key=lambda s: s[1])
        bot.send_message(message.chat.id,
                         f"""Погода в городе {weather["name"]}:
Температура: {round(weather["main"]["temp"])}°
Ощущается как: {round(weather["main"]["feels_like"])}°
Скорость ветра: {float(weather["wind"]["speed"])} м/с, {wind_direction[0][0]}
Давление: {round(float(weather["main"]["pressure"]) / 1.333)} мм рт. ст.
Влажность: {round(weather["main"]["humidity"])}%
Видимость: {weather["visibility"]}
Описание: {weather["weather"][0]["description"]}""", reply_markup=main_markup)
    except Exception:
        bot.send_message(message.chat.id, f"Город {city_name} не найден", reply_markup=main_markup)
