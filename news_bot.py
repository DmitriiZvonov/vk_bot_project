import feedparser
import requests
import random
import schedule
import time
from bs4 import BeautifulSoup
from googletrans import Translator

# 🔹 RSS-ленты новостей о Дубае
RSS_FEEDS = [
    "https://gulfnews.com/rss",
    "https://www.khaleejtimes.com/rss"
]

# 🔹 URL RussianEmirates (парсим вручную)
RUSSIAN_EMIRATES_URL = "https://russianemirates.com/news/"

# 🔹 API VK
VK_API_TOKEN = "vk1.a.GpXji44Pfs8CvNddLvUvBTFegnCSf9q5_uzhryyLzEV_3dJ9WoJmC58mfp0oN1x7y7yWluIJvrhK0iFIGnMw44P1ac16ofEup3solM3mCVG0Td5GiRxB3NbTzLyvjLqAbvHqlDQqkXXn6ODvm58n9cW3XLNYhQ92lv2ENzlMIr_TOgJzeroL53IbxRQ_47MqYb8ctTIcKx36zN36BuMUmA"
GROUP_ID = "228816972"
VK_API_URL = "https://api.vk.com/method/wall.post"
VK_API_VERSION = "5.131"

# 🔹 Инициализация переводчика
translator = Translator()

# 🔹 Хештеги
GENERAL_HASHTAGS = ["#Дубай", "#ОАЭ", "#новости", "#жизньвдубае"]

def extract_image(entry):
    """Пытается найти изображение в новости RSS"""
    if "media_content" in entry:
        return entry.media_content[0]['url']
    return None

def parse_russian_emirates():
    """Парсит новости с RussianEmirates.com"""
    news_list = []
    response = requests.get(RUSSIAN_EMIRATES_URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("div", class_="item")[:5]

        for article in articles:
            title = article.find("div", class_="title").text.strip()
            link = "https://russianemirates.com" + article.find("a")["href"]
            image = article.find("img")["src"] if article.find("img") else None

            title_ru = title  # RussianEmirates уже на русском

            news_list.append({
                "title": title_ru,
                "summary": "",
                "link": link,
                "image": image,
                "hashtags": " ".join(GENERAL_HASHTAGS)
            })

    return news_list

def get_latest_news():
    """Парсит новости из RSS-лент и RussianEmirates"""
    news_list = []

    # 🔹 RSS-новости
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            title = entry.title
            summary = entry.summary
            link = entry.link
            image_url = extract_image(entry)

            try:
                title_ru = translator.translate(title, dest='ru').text
                summary_ru = translator.translate(summary, dest='ru').text
            except Exception as e:
                print(f"Ошибка перевода: {e}")
                continue  # Пропускаем новость, если ошибка перевода

            # 🔹 Добавление новости
            news_list.append({
                "title": title_ru,
                "summary": summary_ru,
                "link": link,
                "image": image_url,
                "hashtags": " ".join(GENERAL_HASHTAGS)
            })

    # 🔹 Новости с RussianEmirates
    news_list.extend(parse_russian_emirates())

    return news_list

def post_news_to_vk(news):
    """Публикует новость в VK"""
    message = f"📢 {news['title']}\n\n{news['summary']}\n🔗 {news['link']}\n\n{news['hashtags']}"

    params = {
        "access_token": VK_API_TOKEN,
        "owner_id": f"-{GROUP_ID}",
        "message": message,
        "v": VK_API_VERSION
    }

    if news["image"]:
        # 🔹 Загружаем изображение на VK сервер
        upload_server = requests.get("https://api.vk.com/method/photos.getWallUploadServer",
                                     params={"access_token": VK_API_TOKEN, "group_id": GROUP_ID, "v": VK_API_VERSION}).json()

        if "response" in upload_server:
            image_url = news["image"]
            upload_url = upload_server["response"]["upload_url"]
            image_data = requests.get(image_url).content
            files = {"photo": ("image.jpg", image_data, "image/jpeg")}

            upload_response = requests.post(upload_url, files=files).json()

            if "photo" in upload_response:
                save_photo = requests.post("https://api.vk.com/method/photos.saveWallPhoto", params={
                    "access_token": VK_API_TOKEN,
                    "group_id": GROUP_ID,
                    "photo": upload_response["photo"],
                    "server": upload_response["server"],
                    "hash": upload_response["hash"],
                    "v": VK_API_VERSION
                }).json()

                if "response" in save_photo:
                    photo_id = save_photo["response"][0]["id"]
                    owner_id = save_photo["response"][0]["owner_id"]
                    params["attachments"] = f"photo{owner_id}_{photo_id}"

    response = requests.post(VK_API_URL, params=params).json()

    if "response" in response:
        print("✅ Новость успешно опубликована в VK!")
    else:
        print(f"❌ Ошибка при публикации: {response}")

def job():
    """Основная задача: публикация новостей каждые 3 часа"""
    print("🔹 Получаем свежие новости...")
    latest_news = get_latest_news()

    if not latest_news:
        print("❌ Нет свежих новостей для публикации.")
        return

    selected_news = random.sample(latest_news, min(3, len(latest_news)))  # Публикуем 3 случайные новости

    for news in selected_news:
        print(f"📰 Публикуем новость: {news['title']}")
        post_news_to_vk(news)
        time.sleep(10)  # Небольшая пауза между постами

# 🔹 Запускаем задачу каждые 3 часа
schedule.every(3).hours.do(job)

if __name__ == "__main__":
    print("📰 Бот новостей запущен и будет публиковать каждые 3 часа...")
    job()  # Выполнить сразу при запуске

    while True:
        schedule.run_pending()
        time.sleep(60)
