import datetime
import json
import logging
import os
from functools import wraps
from typing import Optional

import pandas as pd
from pandas.tseries.offsets import DateOffset

from src.views import excel_read

# operations = excel_read('../data/operations.xlsx')
# df = pd.DataFrame(operations)

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
log_path = os.path.join(project_root, "logs", "reports.log")
file_handler = logging.FileHandler(log_path, mode="w")
file_formater = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: - %(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def param_deco(filename):
    """Декоратор записи результата работы функции в файл"""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                if isinstance(result, pd.DataFrame):
                    # Для DataFrame используем to_json
                    result.to_json(filename, orient="records", force_ascii=False, indent=4)
                else:
                    # Для остальных типов — записываем как JSON
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump({"result": result, "type": type(result).__name__}, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчёт успешно сохранён в файл: {filename}")
            except AttributeError:
                logger.error(f"Ошибка: результат функции не является DataFrame. Не удалось сохранить в {filename}")
            except PermissionError:
                logger.error(f"Ошибка доступа: нет прав для записи в файл {filename}")
            except Exception as e:
                logger.warning(f"Произошла непредвиденная ошибка при сохранении в {filename}: {e}")
            return result

        return inner

    return wrapper


@param_deco("../deco_result.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца"""
    if date is None:
        # date_obj = datetime.date.today() # строка если фильтруем от сегодняшней даты
        date_obj = datetime.date(2021, 12, 31)  # дата 31.12.2021
    else:
        date_obj = datetime.datetime.strptime(date, "%d.%m.%Y").date()
    date_timestamp = pd.Timestamp(date_obj)
    end_date = date_timestamp.date()
    start_date = (date_timestamp - DateOffset(months=3)).date()
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], dayfirst=True)

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], dayfirst=True, errors="coerce"  # заменяет некорректные даты на NaT
    )

    filtered_df = transactions[
        (transactions["Дата операции"].dt.date >= start_date)
        & (transactions["Дата операции"].dt.date <= end_date)
        & (transactions["Категория"] == category)
    ]

    filtered_df["Сумма операции"] = pd.to_numeric(filtered_df["Сумма операции"], errors="coerce")
    total_spending = filtered_df["Сумма операции"].sum()
    result_df = pd.DataFrame({"Суммарные траты": [total_spending]})
    return result_df


#
# if __name__ == '__main__':
#     print(spending_by_category(df, 'Супермаркеты', '31.10.2019'))
