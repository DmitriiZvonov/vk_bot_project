import requests
import time
import logging

# Настройка логирования
logging.basicConfig(
    filename="bot.log",  # Имя файла лога
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат записи
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат времени
)

# Ваш API-токен сообщества
VK_API_TOKEN = "vk1.a.v6redrSc43L4VJjSUNdxT8ckDAEvQDrMb92J_o3mLWs_X5BiwI4px2l33eOulYgAqG0bGK9u0GCHgARF5fxJcnwXz0aYa7dirJmfb8jjRNIV1s-9cpcMr0KJsNn64qfHKHAuwQBGsLFNk-HzXA1SKXfdsK8j4fo7lkfwaMl0kZVjHcR8xedi3gNHU4rjRkQGAuBGQpIq6x4cdY5xpJNbVA"
# ID сообщества
GROUP_ID = "228816972"

# URL для работы с VK API
VK_API_URL = "https://api.vk.com/method/"
API_VERSION = "5.131"

def get_long_poll_server():
    """Получает настройки Long Poll сервера."""
    url = f"{VK_API_URL}groups.getLongPollServer"
    params = {
        "access_token": VK_API_TOKEN,
        "group_id": GROUP_ID,
        "v": API_VERSION
    }
    response = requests.get(url, params=params).json()
    if "response" in response:
        return response["response"]
    else:
        logging.error(f"Ошибка получения Long Poll сервера: {response}")
        raise Exception(f"Ошибка получения Long Poll сервера: {response}")

def send_message(user_id, message):
    """Отправляет сообщение пользователю и логирует результат."""
    url = f"{VK_API_URL}messages.send"
    params = {
        "access_token": VK_API_TOKEN,
        "user_id": user_id,
        "message": message,
        "random_id": int(time.time() * 1000),  # Уникальный ID для сообщения
        "v": API_VERSION
    }
    response = requests.post(url, params=params).json()
    if "response" in response:
        logging.info(f"Сообщение отправлено пользователю {user_id}: {message}")
        print(f"Сообщение отправлено пользователю {user_id}")
    else:
        logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {response}")
        print(f"Ошибка отправки сообщения: {response}")

def handle_new_subscriber(user_id):
    """Обрабатывает нового подписчика."""
    welcome_message = (
        "🎉 Добро пожаловать в сообщество \"Дубай на ладони\"!\n\n"
        "Меня зовут Дмитрий, и я рад, что вы присоединились. Здесь вы найдёте:\n"
        "🌍 Полезные советы по жизни и отдыху в Дубае.\n"
        "💡 Уникальные лайфхаки, а также помощь в шопинге, экскурсиях и бизнесе.\n\n"
        "Напишите, если у вас есть вопросы — всегда рады помочь!"
    )
    try:
        send_message(user_id, welcome_message)
    except Exception as e:
        logging.error(f"Ошибка при отправке приветственного сообщения пользователю {user_id}: {e}")
        print(f"Ошибка при отправке сообщения: {e}")

def listen_to_long_poll():
    """Слушает Long Poll сервер и обрабатывает новые события."""
    server_data = get_long_poll_server()
    server = server_data["server"]
    if not server.startswith("https://"):
        server = f"https://{server}"
    key = server_data["key"]
    ts = server_data["ts"]

    print("Бот запущен и слушает события...")
    while True:
        try:
            response = requests.get(server, params={
                "act": "a_check",
                "key": key,
                "ts": ts,
                "wait": 25
            }).json()

            if "failed" in response:
                logging.warning(f"Ошибка Long Poll: {response}. Перезапуск...")
                server_data = get_long_poll_server()
                server = server_data["server"]
                if not server.startswith("https://"):
                    server = f"https://{server}"
                key = server_data["key"]
                ts = server_data["ts"]
                continue

            # Обрабатываем новые события
            ts = response["ts"]
            updates = response.get("updates", [])
            for event in updates:
                if event["type"] == "group_join":  # Подписка на сообщество
                    user_id = event["object"]["user_id"]
                    logging.info(f"Новый подписчик: {user_id}")
                    print(f"Новый подписчик: {user_id}")
                    handle_new_subscriber(user_id)

        except Exception as e:
            logging.error(f"Ошибка: {e}")
            time.sleep(5)  # Ждем перед повторной попыткой

if __name__ == "__main__":
    listen_to_long_poll()
