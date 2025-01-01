# Импорты библиотек
import os
import requests
from telethon import TelegramClient, events
from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from apscheduler.schedulers.blocking import BlockingScheduler

# Настройки Telegram API
TELEGRAM_API_ID = '21057835'
TELEGRAM_API_HASH = '3b2217a74fe0283b89000debee1053a7'
TELEGRAM_CHANNEL = 'https://t.me/dubai_mid'

# Настройки VK API
VK_ACCESS_TOKEN = 'vk1.a.GpXji44Pfs8CvNddLvUvBTFegnCSf9q5_uzhryyLzEV_3dJ9WoJmC58mfp0oN1x7y7yWluIJvrhK0iFIGnMw44P1ac16ofEup3solM3mCVG0Td5GiRxB3NbTzLyvjLqAbvHqlDQqkXXn6ODvm58n9cW3XLNYhQ92lv2ENzlMIr_TOgJzeroL53IbxRQ_47MqYb8ctTIcKx36zN36BuMUmA'
VK_GROUP_ID = '228816972'

# Создание клиентов
telegram_client = TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH)
vk_session = VkApi(token=VK_ACCESS_TOKEN)
vk = vk_session.get_api()
vk_upload = VkUpload(vk_session)

# Функция для публикации поста в ВК
def post_to_vk(message_text, file_paths):
    attachments = []

    # Загрузка фото/файлов в ВК
    for file_path in file_paths:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            photo = vk_upload.photo_wall(photos=[file_path], group_id=VK_GROUP_ID)
            attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
        else:
            # Для других файлов можно добавить логику (например, docs.getUploadServer)
            pass

    # Публикация поста
    vk.wall.post(
        owner_id=f"-{VK_GROUP_ID}",
        message=message_text,
        attachments=','.join(attachments),
        from_group=1,
        random_id=get_random_id()
    )

# Функция для обработки новых сообщений из Telegram
def process_telegram_messages():
    async def main():
        await telegram_client.start()
        async for message in telegram_client.iter_messages(TELEGRAM_CHANNEL):
            message_text = message.text or ""
            file_paths = []

            # Скачивание вложений
            if message.media:
                file_path = await telegram_client.download_media(message.media)
                file_paths.append(file_path)

            # Публикация в ВК
            post_to_vk(message_text, file_paths)

            # Удаление временных файлов
            for path in file_paths:
                os.remove(path)

    telegram_client.loop.run_until_complete(main())

# Настройка планировщика для автоматизации
scheduler = BlockingScheduler()
scheduler.add_job(process_telegram_messages, 'interval', hours=24)  # Запускать раз в день

print("Бот запущен и ожидает выполнения задач...")
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Бот остановлен.")
