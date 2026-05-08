import re
import json
from src.views import excel_read

operations = excel_read('../data/operations.xlsx')


def cashback_cat(data: list[dict], year: str, month: str) -> json:
    """Функция подсчета кэшбэка по категориям за указанный месяц"""
    category_cashback = {}
    for operation in data:
        date_operation = operation.get('Дата операции')
        if date_operation and date_operation[3:5] == month and date_operation[6:10] == year:
            category = operation.get('Категория')
            cashback_amount = operation.get('Бонусы (включая кэшбэк)')
            if category and cashback_amount:
                if category in category_cashback:
                    category_cashback[category] += cashback_amount
                else:
                    category_cashback[category] = cashback_amount

    return json.dumps(category_cashback, ensure_ascii=False)

def easy_finder(data: list[dict]) -> json:
    found_transactions = []
    search_word = input("Введите слово для поиска: ").lower().strip()
    for transaction in data:
        category = transaction.get('Категория', '')
        description = transaction.get('Описание', '')
        # Приводим значения к нижнему регистру для поиска без учёта регистра
        if (search_word in str(category).lower()) or (search_word in str(description).lower()):
            found_transactions.append(transaction)

    json_data = json.dumps(found_transactions, ensure_ascii=False, indent=2)
    return json_data



def find_transaction(data: list[dict]):
    """Функция поиска транзакций по номеру телефона"""
    new_transact = []
    for operation in data:
        find_param = re.findall(r'\+\d\s\d{3}\s\d{3}-\d{2}-\d{2}',operation.get('Описание', ''))
        find_param_2 = re.findall(r'\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}', operation.get('Описание', ''))
        find_param_3 = re.findall(r'8\d{10}$', operation.get('Описание', ''))
        if find_param or find_param_2 or find_param_3:
            new_transact.append(operation)

    json_data = json.dumps(new_transact, ensure_ascii=False)

    return json_data

# if __name__ == '__main__':
    # print(find_transaction(operations))
#     print(cashback_cat(operations,'2021','12'))
#     print(easy_finder(operations))
