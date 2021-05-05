import telebot

static_api_server = "https://static-maps.yandex.ru/1.x/"
geocode_api_server = "https://geocode-maps.yandex.ru/1.x/"
places_api_server = "https://search-maps.yandex.ru/v1/"
static_params = {
    "l": "map",
}
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "format": "json",
    "results": 1
}
places_params = {
    "lang": "ru_RU",
    "apikey": "575a0baa-461e-472c-8be2-bb4234d97a53",
    "results": 1
}
format_keys = {"g": "geocode", "geocode": "geocode", "геокод": "geocode", "l": "l", "layer": "l", "слой": "l", "z": "z",
               "zoom": "z", "масштаб": "z", "s": "scale", "scale": "scale", "увеличение": "scale", "m": "pt",
               "marker": "pt", "метка": "pt", "k": "kind", "kind": "kind", "p": "text", "place": "text",
               "место": "text", "r": "results", "results": "results", "результаты": "results"}
format_values = {"sat": "sat", "спутник": "sat", "map": "map", "схема": "map", "sat,skl": "sat,skl",
                 "sat,map": "sat,skl", "hybrid": "sat,skl", "гибрид": "sat,skl", "map,trf": "map,trf",
                 "sat,trf": "sat,trf", "sat,skl,trf": "sat,skl,trf", "house": "house", "street": "street",
                 "metro": "metro", "district": "district", "locality": "locality"
                 }
format_kind = {"🏠дом": "house", "дом": "house", "🛣улица": "street", "улица": "", "🚇метро": "metro",
               "метро": "metro", "🏙район": "district", "район": "district", "🏘населенный пункт": "locality",
               "населенный пункт": "locality"
               }
TOKEN = "1719349692:AAHNGDF0WeCkGXy3Ef8uWuYXtWmzQF4VypE"
HEROKU_APP_NAME = "map-service-bot"
url = 'http://api.openweathermap.org/data/2.5/weather'
api_weather = 'e4a3da131fe7dd1aa4d06d1ded5c6963'
bot = telebot.TeleBot(TOKEN)
