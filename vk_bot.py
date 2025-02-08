import requests
import xml.etree.ElementTree as ET

# Ваш API-токен сообщества
VK_API_TOKEN = "vk1.a.u9v_PWhvCEyOkPfYa5X0ZTgrGkbhGj84iC9tXR-3rrZqoxm4nZk0hmMBzFQ6R5Rbfkj2V5B4tu1IZtAbxZIGkS1OJ3yyVRMjObmyMUfpFl4aycGzx_LSlePnJk8vyD-TO6wz5GVoHmx8sPr-R3vXPVuLduokaKI0yxOaOf_7Ct80FxACixbFXJX128qrMsgXQJXZkzxxYTHW3cRdh2ShMw"
# ID сообщества
GROUP_ID = "228816972"

# URL для отправки сообщений через API VK
VK_API_URL = "https://api.vk.com/method/wall.post"

# URL API Центробанка России
CBR_API_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

# Константа курса AED → USD
AED_TO_USD = 0.272294  # Фиксированный курс дирхама к доллару

# Версия API VK
API_VERSION = "5.131"

HASHTAGS = "#КурсВалют #AEDRUB #ДирхамРубль #КурсДирхама #ОбменВалют #Финансы #Деньги #ОАЭ #Дубай #Экономика"

def get_usd_to_rub():
    """Получает курс доллара к рублю (USD → RUB) из Центробанка России."""
    response = requests.get(CBR_API_URL)
    if response.status_code == 200:
        # Разбираем XML-ответ
        tree = ET.fromstring(response.content)
        for currency in tree.findall("Valute"):
            char_code = currency.find("CharCode").text
            if char_code == "USD":
                value = currency.find("Value").text
                # Курс возвращается как строка с запятой (например, '75,45')
                return float(value.replace(",", "."))
        raise ValueError("Не удалось найти курс USD → RUB в ответе от Центробанка.")
    else:
        raise ConnectionError(f"Ошибка при подключении к API Центробанка: {response.status_code}")

def calculate_aed_to_rub():
    """Рассчитывает курс AED → RUB через фиксированный AED → USD и USD → RUB."""
    try:
        usd_to_rub = get_usd_to_rub()
        return AED_TO_USD * usd_to_rub
    except Exception as e:
        print(f"Ошибка при расчете курса: {e}")
        raise

def post_message_to_vk(message):
    """Отправляет сообщение на стену сообщества."""
    params = {
        "access_token": VK_API_TOKEN,
        "owner_id": f"-{GROUP_ID}",  # Отрицательный ID для сообщества
        "message": message,
        "v": API_VERSION
    }
    response = requests.post(VK_API_URL, params=params)
    if response.status_code == 200:
        print("Сообщение успешно отправлено:", response.json())
    else:
        print("Ошибка при отправке сообщения:", response.text)

# Основная логика
if __name__ == "__main__":
    try:
        # Рассчитываем курс дирхама к рублю
        exchange_rate = calculate_aed_to_rub()
        message = f"Текущий курс дирхама (AED) к рублю (RUB): {exchange_rate:.2f}\n\n{HASHTAGS}"
        
        # Отправляем сообщение в VK
        post_message_to_vk(message)
    except Exception as e:
        print(f"Произошла ошибка: {e}")