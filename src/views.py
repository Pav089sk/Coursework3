import datetime
import json
from typing import Any
import pandas as pd
import requests
from twelvedata import TDClient


def get_day(day_time: str) -> str:
    """Функция принимает строку в формате YYYY-MM-DD HH:MM:SS для корректного приветствия"""
    day_object = datetime.datetime.strptime(day_time, "%Y-%m-%d %H:%M:%S")
    time_only = day_object.time()
    if datetime.time(6, 0, 0) <= time_only <= datetime.time(11, 59, 59):
        answer = "Доброе утро"
    elif datetime.time(12, 0, 0) <= time_only <= datetime.time(17, 59, 59):
        answer = "Добрый день"
    elif datetime.time(18, 0, 0) <= time_only <= datetime.time(22, 59, 59):
        answer = "Добрый вечер"
    else:
        answer = "Доброй ночи"

    return answer


def excel_read(path_excel: str) -> pd.DataFrame:
    """Функция принимает путь до excel файла
    и возвращает DataFrame"""
    excel_data = pd.read_excel(path_excel)
    return excel_data


# operations = excel_read('../data/operations.xlsx')


def card_stat(df: pd.DataFrame) -> list:
    """Функция возвращает последние цифры карты, общую сумму расходов и кэшбэк"""
    # 1. Фильтрация: убираем строки с отсутствующим номером карты
    df_filtered = df[df["Номер карты"].notna()].copy()
    # 2. Извлекаем последние 4 цифры номера карты (убираем звёздочки)
    df_filtered["last_digits"] = df_filtered["Номер карты"].str.replace("*", "", regex=False)
    # 3. Обрабатываем сумму операции: берём модуль для отрицательных значений, иначе — 0
    df_filtered["amount"] = df_filtered["Сумма операции"].apply(lambda x: abs(x) if x < 0 else 0)
    # 4. Заполняем пропущенные значения кэшбека нулями
    df_filtered["cashback"] = df_filtered["Кэшбэк"].fillna(0)
    # 5. Группируем по последним 4 цифрам карты и суммируем расходы и кэшбэк
    grouped = df_filtered.groupby("last_digits").agg({"amount": "sum", "cashback": "sum"}).reset_index()
    # 6. Округляем результаты до 2 знаков после запятой
    grouped["amount"] = grouped["amount"].round(2)
    grouped["cashback"] = grouped["cashback"].round(2)
    # 7. Преобразуем в список словарей для совместимости с исходной функцией
    result_list = grouped.rename(columns={"amount": "total_spent", "cashback": "cashback"}).to_dict("records")

    return result_list


def top_transactions(df: pd.DataFrame) -> list:
    """Функция отдаёт топ‑5 транзакций по сумме платежа"""
    # 1. Фильтрация: убираем строки с отсутствующей суммой платежа
    df_filtered = df[df["Сумма платежа"].notna()].copy()
    # 2. Обрабатываем сумму платежа: заменяем NaN на 0, берём модуль
    df_filtered["amount"] = df_filtered["Сумма платежа"].fillna(0).abs()
    # 3. Выбираем нужные столбцы и переименовываем их
    result_df = df_filtered[["Дата платежа", "Сумма платежа", "Категория", "Описание"]].rename(
        columns={"Дата платежа": "date", "Сумма платежа": "amount", "Категория": "category", "Описание": "description"}
    )
    # Добавляем столбец с модулем суммы (уже обработанной)
    result_df["amount"] = df_filtered["amount"]
    # 4. Сортируем по убыванию суммы платежа
    sorted_df = result_df.sort_values("amount", ascending=False)
    # 5. Берём топ‑5 строк
    top_5_df = sorted_df.head(5)
    # 6. Преобразуем в список словарей для совместимости с исходной функцией
    return top_5_df.to_dict("records")


def user_settings_import(data: str) -> Any:
    """Функция открывает файл с пользовательскими настройками"""
    with open(data) as file:
        res = json.load(file)
    return res


# не применяю для простоты проверки работы
# load_dotenv()
# API_KEY = os.getenv("Your_API_Key")


def convert(operation: dict) -> dict:
    """Функция для возврата курса валют"""
    currencies_list = operation.get("user_currencies", {})
    url = "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {"error": f"Ошибка API: HTTP {response.status_code}", "currency_rates": []}

        data = response.json()
        currency_rates = []
        api_dict = data.get("conversion_rates")

        if not api_dict:
            return {"error": "Не получены данные о курсах валют от API", "currency_rates": []}

        for currency in currencies_list:
            rate = api_dict.get(currency)
            if rate is not None:
                try:
                    currency_rates.append({"currency": currency, "rate": round((1 / rate), 2)})
                except ZeroDivisionError or TypeError:
                    # Обрабатываем случай, если rate = 0 или некорректный тип
                    continue

        return {"currency_rates": currency_rates}

    except requests.exceptions.Timeout:
        return {"error": "Превышено время ожидания ответа от сервера", "currency_rates": []}
    except requests.exceptions.ConnectionError:
        return {"error": "Ошибка подключения к серверу (проблемы с интернетом)", "currency_rates": []}
    except requests.exceptions.RequestException as e:
        return {"error": f"Общая ошибка запроса: {str(e)}", "currency_rates": []}
    except (KeyError, ValueError, TypeError) as e:
        return {"error": f"Ошибка обработки данных: {str(e)}", "currency_rates": []}


# API_KEY_ = os.getenv("API_KEY_STOCKS")
# Функция ниже обращается к API запрос к которой не выполняется без прямого указания ключа


def stocks_price(stocks: dict) -> dict:
    """Функция для запроса стоимости акций"""
    stock_list = stocks.get("user_stocks", {})
    errors = []

    try:
        td = TDClient(apikey="0db2a2bf0a56477f96d16463562ff8ed")
        stock_prices = []

        for stock in stock_list:
            try:
                price_data = td.price(symbol=stock).as_json()

                if "price" not in price_data:
                    errors.append(f"Для {stock}: не найдено поле 'price' в ответе API")
                    continue

                price = price_data["price"]
                if price is None:
                    errors.append(f"Для {stock}: получено значение None для цены")
                    continue
                try:
                    price_fl = round(float(price), 2)
                    stock_prices.append({"stock": stock, "price": price_fl})
                except (ValueError, TypeError) as e:
                    errors.append(f"Для {stock}: ошибка преобразования цены в число — {str(e)}")
                    continue

            except Exception as e:
                errors.append(f"Для {stock}: общая ошибка запроса — {str(e)}")
                continue

    except Exception as e:
        # Ошибка инициализации клиента или критическая ошибка
        return {"error": f"Критическая ошибка при работе с API: {str(e)}", "stock_prices": [], "errors": errors}

    result = {"stock_prices": stock_prices}
    if errors:
        result["errors"] = errors

    return result


# if __name__ == "__main__":
#         print(get_day("2025-06-17 23:45:21"))
#         print(excel_read('../data/operations.xlsx'))
#         print(card_stat(excel_read('../data/operations.xlsx')))
#         # print(top_transactions(operations))
#         print(user_settings_import('../user_settings.json'))
#         # json.dumps(result_list, ensure_ascii=False, indent=2)
#         print(convert(user_settings_import("../user_settings.json")))
#         print(stocks_price((user_settings_import('../user_settings.json'))))
#         print(convert(user_settings_import('../user_settings.json')))
