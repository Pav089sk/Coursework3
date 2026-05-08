import datetime
import pandas as pd
import json
import math


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


operations = excel_read('../data/operations.xlsx')


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

        # Добавляем транзакцию в список
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


# if __name__ == '__main__':
#     # print(get_day("2025-06-17 23:45:21"))
#     print(excel_read('../data/operations.xlsx'))
#     print(card_stat(operations))
#     print(top_transactions(operations))

# json.dumps(result_list, ensure_ascii=False, indent=2)