import datetime
import pandas as pd
import json
import math
import requests
import os
from dotenv import load_dotenv
from twelvedata import TDClient


def get_day(day_time: str):
    """Функция принимает строку в формате YYYY-MM-DD HH:MM:SS для корректного приветствия"""
    day_object = datetime.datetime.strptime(day_time, "%Y-%m-%d %H:%M:%S")
    time_only = day_object.time()
    if datetime.time(6, 0, 0) <= time_only <= datetime.time(11, 59, 59):
        answer = 'Доброе утро'
    elif datetime.time(12, 0, 0) <= time_only <= datetime.time(17, 59, 59):
        answer = 'Добрый день'
    elif datetime.time(18, 0, 0) <= time_only <= datetime.time(22, 59, 59):
        answer = 'Добрый вечер'
    else:
        answer = 'Доброй ночи'

    return answer

def excel_read(path_excel: str) -> list:
    """Функция принимает путь до excel файла
    и возвращает список словарей из строк файла"""
    excel_data = pd.read_excel(path_excel).to_dict("records")
    return excel_data


# operations = excel_read('../data/operations.xlsx')


def card_stat(data: list[dict]):
    """Функция возвращает последние цифры карты общую сумму расходов и кэшбэк"""
    cards_data = {}
    for transaction in data:
        card_number = transaction.get('Номер карты')
        if not card_number or card_number != card_number:  # проверка на nan
            continue
        last_4_digits = card_number.replace('*', '')
        amount = transaction.get('Сумма операции', 0)
        if amount < 0:
            amount = abs(amount)
        else:
            amount = 0
        cashback = transaction.get('Кэшбэк', 0)
        if cashback != cashback:  # проверка на nan
            cashback = 0
        if last_4_digits not in cards_data:
            cards_data[last_4_digits] = {
                'last_digits': last_4_digits,
                'total_spent': 0,
                'cashback': 0
            }
        cards_data[last_4_digits]['total_spent'] += round(amount, 2)
        cards_data[last_4_digits]['cashback'] += cashback
        for card in cards_data.values():
            card['total_spent'] = round(card['total_spent'], 2)
            card['cashback'] = round(card['cashback'], 2)

    result_list = list(cards_data.values())
    return result_list

def top_transactions(data: list[dict]):
    """Функция отдаёт топ 5 транзакций по сумме платежа"""
    processed_transactions = []
    for transaction in data:
        amount = transaction.get('Сумма платежа')
        if amount is None:
            continue
        if isinstance(amount, float) and math.isnan(amount):
            amount = 0
        amount_abs = abs(amount)
        date = transaction.get('Дата платежа', '')
        category = transaction.get('Категория', '')
        description = transaction.get('Описание', '')
        processed_transactions.append({
            'date': date,
            'amount': amount_abs,
            'category': category,
            'description': description
        })
    sorted_transactions = sorted(
        processed_transactions,
        key=lambda x: x['amount'],
        reverse=True
    )
    top_5 = sorted_transactions[:5]
    result = {'top_transactions': top_5}
    return result

def user_settings_import(data):
    """Функция открывает файл с пользовательскими настройками"""
    with open(data) as file:
        res = json.load(file)
    return res

load_dotenv()
API_KEY = os.getenv("Your_API_Key")

def convert(operation):
    """Функция для возврата курса валют"""
    currencies_list = operation.get("user_currencies", {})
    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB'
    response = requests.get(url)
    data = response.json()
    currency_rates =[]
    api_dict = data.get("conversion_rates")
    for currency in currencies_list:
        rate = api_dict.get(currency)
        if rate is not None:
            currency_rates.append({
                "currency":currency,
                "rate": round((1 / rate), 2)
            })
    # Формируем итоговый JSON в нужном формате
    result = {
        "currency_rates": currency_rates
    }
    # Преобразуем словарь в строку JSON с отступами для читаемости
    json_output = json.dumps(result, indent=2)

    return json_output

# API_KEY_ = os.getenv("API_KEY_STOCKS")
# Функция ниже обращается к API запрос к которой не выполняется без прямого указания ключа

def stocks_price(stocks):
    stock_list = stocks.get("user_stocks", {})
    td = TDClient(apikey="0db2a2bf0a56477f96d16463562ff8ed")
    stock_prices = []
    for stock in stock_list:
        try:
            price_data = td.price(symbol=stock).as_json()
            if "price" in price_data:
                price = price_data["price"]
            else:
                print(
                    f"Предупреждение: в ответе для {stock} не найдено поле 'price'. Полный ответ: {price_data}")
                continue

            # Добавляем объект с названием акции и ценой в итоговый список
            stock_prices.append({
                "stock": stock,
                "price": price
            })
        except Exception as e:
            print(f"Ошибка при получении цены для {stock}: {e}")

    result = {
        "stock_prices": stock_prices
    }

    json_output = json.dumps(result, indent=2)

    return json_output


# if __name__ == '__main__':
#     print(get_day("2025-06-17 23:45:21"))
#     print(excel_read('../data/operations.xlsx'))
#     print(card_stat(operations))
#     print(top_transactions(operations))
#     print(user_settings_import('../user_settings.json'))
#     json.dumps(result_list, ensure_ascii=False, indent=2)
#     print(convert(user_settings_import('../user_settings.json')))
#     print(stocks_price((user_settings_import('../user_settings.json'))))
#     print(convert(user_settings_import('../user_settings.json')))