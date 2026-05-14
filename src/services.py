from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any
import json
import pandas as pd

import re

def cashback_cat(data: list[dict], year: str, month: str) -> str:
    """Функция подсчета кэшбэка по категориям за указанный месяц"""
    # Шаг 1: Фильтрация по дате
    date_filtered = filter(
        lambda op: (
            op['Дата операции'].year == year and
            op['Дата операции'].month == month
        ),
        data
    )
    # Шаг 2: Фильтрация транзакций с кэшбеком
    cashback_filtered = filter(
        lambda op: op.get('Бонусы (включая кэшбэк)') is not None,
        date_filtered
    )
    # Шаг 3: Агрегация по категориям
    category_cashback: defaultdict[str, float] = defaultdict(float)
    for operation in cashback_filtered:
        category = operation.get('Категория')
        cashback_amount = operation.get('Бонусы (включая кэшбэк)')
        if category and cashback_amount:
            category_cashback[category] += cashback_amount

    # Шаг 4: Сортировка и JSON
    sorted_categories = sorted(
        category_cashback.items(),
        key=lambda item: item[1],
        reverse=True
    )
    return json.dumps(
        dict(sorted_categories),
        indent=2,
        ensure_ascii=False
    )


def easy_finder(data: List[Dict[str, Any]]) -> str:
    """Функция простого поиска транзакций по строке"""
    search_word = input("Введите слово для поиска: ").lower().strip()
    # Фильтрация транзакций через filter и лямбда‑функцию
    found_transactions = list(filter(
        lambda transaction: (
            search_word in str(transaction.get("Категория", "")).lower() or
            search_word in str(transaction.get("Описание", "")).lower()
        ),
        data
    ))
    return json.dumps(found_transactions, ensure_ascii=False, indent=2)


def find_transaction(data: List[Dict[str, Any]]) -> str:
    """Функция поиска транзакций по номеру телефона"""
    # Объединяем все регулярные выражения в одно для эффективности
    phone_pattern = re.compile(
        r'(\+\d\s\d{3}\s\d{3}-\d{2}-\d{2}|'
        r'\+7\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}|'
        r'8\d{10})$'
    )
    # Фильтрация транзакций через filter и лямбда‑функцию
    found_transactions = list(filter(
        lambda operation: bool(
            phone_pattern.search(operation.get("Описание", ""))
        ),
        data
    ))
    return json.dumps(found_transactions, ensure_ascii=False, indent=2)


# if __name__ == '__main__':
#     print(find_transaction(operations))
# print(cashback_cat(operations,'2021','12'))
#     print(easy_finder(operations))
