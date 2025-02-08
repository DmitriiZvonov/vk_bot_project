import requests
import schedule
import time

# 🔹 Ваш API-ключ OpenWeatherMap (https://openweathermap.org/)
WEATHER_API_KEY = "1faa01402c157e4cf083b134f816f312"

# 🔹 Ваш API-токен сообщества VK
VK_API_TOKEN = "vk1.a.u9v_PWhvCEyOkPfYa5X0ZTgrGkbhGj84iC9tXR-3rrZqoxm4nZk0hmMBzFQ6R5Rbfkj2V5B4tu1IZtAbxZIGkS1OJ3yyVRMjObmyMUfpFl4aycGzx_LSlePnJk8vyD-TO6wz5GVoHmx8sPr-R3vXPVuLduokaKI0yxOaOf_7Ct80FxACixbFXJX128qrMsgXQJXZkzxxYTHW3cRdh2ShMw"
GROUP_ID = "228816972"

# 🔹 URL API для погоды (Дубай, ОАЭ)
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
CITY = "Dubai"
COUNTRY_CODE = "AE"

# 🔹 URL для отправки сообщений через VK API
VK_API_URL = "https://api.vk.com/method/wall.post"
VK_API_VERSION = "5.131"

# 🔹 Хештеги
HASHTAGS = "#ПогодаВДубае #Дубай #ОАЭ #ПрогнозПогоды #DubaiWeather #UAE"

def get_weather():
    """Получает текущую погоду в Дубае"""
    params = {
        "q": f"{CITY},{COUNTRY_CODE}",
        "appid": WEATHER_API_KEY,
        "units": "metric",  # Температура в градусах Цельсия
        "lang": "ru"
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]  # Температура сейчас
        feels_like = data["main"]["feels_like"]  # Ощущается как
        humidity = data["main"]["humidity"]  # Влажность
        wind_speed = data["wind"]["speed"]  # Скорость ветра
        weather_desc = data["weather"][0]["description"].capitalize()  # Описание погоды

        return {
            "temp": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather_desc": weather_desc
        }
    else:
        print(f"Ошибка при получении текущей погоды: {data}")
        return None

def get_forecast():
    """Получает прогноз погоды на день"""
    params = {
        "q": f"{CITY},{COUNTRY_CODE}",
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
        "cnt": 4  # Берем 4 ближайших прогноза (примерно 12 часов)
    }
    response = requests.get(FORECAST_API_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        temp_min = min([entry["main"]["temp_min"] for entry in data["list"]])  # Минимальная температура
        temp_max = max([entry["main"]["temp_max"] for entry in data["list"]])  # Максимальная температура
        rain_chance = any("rain" in entry["weather"][0]["main"].lower() for entry in data["list"])  # Будет ли дождь?

        forecast_text = f"🌡 Максимальная: {temp_max:.1f}°C | Минимальная: {temp_min:.1f}°C\n"
        forecast_text += "🌧 Вероятность дождя: Да" if rain_chance else "🌤 Дождя не ожидается"

        return forecast_text
    else:
        print(f"Ошибка при получении прогноза: {data}")
        return None

def post_message_to_vk(message):
    """Отправляет сообщение в VK"""
    params = {
        "access_token": VK_API_TOKEN,
        "owner_id": f"-{GROUP_ID}",
        "message": message,
        "v": VK_API_VERSION
    }
    response = requests.post(VK_API_URL, params=params)
    
    if response.status_code == 200 and "response" in response.json():
        print("✅ Прогноз погоды успешно опубликован!")
    else:
        print(f"❌ Ошибка при публикации: {response.text}")

def job():
    """Основная задача: получение текущей погоды и прогноза на день"""
    print("🔹 Получаем текущую погоду и прогноз...")
    
    weather_now = get_weather()
    weather_forecast = get_forecast()
    
    if weather_now and weather_forecast:
        message = (
            f"🌞 Погода в Дубае на сегодня:\n\n"
            f"📍 Сейчас: {weather_now['temp']:.1f}°C (ощущается как {weather_now['feels_like']:.1f}°C)\n"
            f"💨 Ветер: {weather_now['wind_speed']} м/с\n"
            f"💧 Влажность: {weather_now['humidity']}%\n"
            f"🌤️ {weather_now['weather_desc']}\n\n"
            f"🔮 Прогноз на ближайшие часы:\n{weather_forecast}\n\n"
            f"{HASHTAGS}"
        )
        print("🔹 Отправляем прогноз в VK...")
        post_message_to_vk(message)

# Настроить выполнение скрипта в 08:00 утра каждый день
schedule.every().day.at("08:00").do(job)

if __name__ == "__main__":
    print("🌤️ Бот прогноза погоды запущен и ждет 08:00...")
    job()  # Выполнить сразу при запуске

    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверка каждую минуту
