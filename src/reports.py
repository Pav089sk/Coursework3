import pandas as pd
from typing import Optional
from src.views import excel_read
import datetime
from pandas.tseries.offsets import DateOffset

operations = excel_read('../data/operations.xlsx')
df = pd.DataFrame(operations)

def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца"""
    if date is None:
        # date_obj = datetime.date.today() # строка если фильтруем от сегодняшней даты
        date_obj = datetime.date(2021, 12, 31) # дата 31.12.2021
    else:
        date_obj = datetime.datetime.strptime(date, "%d.%m.%Y").date()
    date_timestamp = pd.Timestamp(date_obj)
    end_date = date_timestamp.date()
    start_date = (date_timestamp - DateOffset(months=3)).date()
    transactions['Дата платежа'] = pd.to_datetime(transactions['Дата платежа'], dayfirst=True)

    transactions['Дата операции'] = pd.to_datetime(
        transactions['Дата операции'],
        dayfirst=True,
        errors='coerce'  # заменяет некорректные даты на NaT
    )

    filtered_df = transactions[
        (transactions['Дата операции'].dt.date >= start_date) &
        (transactions['Дата операции'].dt.date <= end_date) &
        (transactions['Категория'] == category)
        ]

    filtered_df['Сумма операции'] = pd.to_numeric(filtered_df['Сумма операции'], errors='coerce')
    total_spending = filtered_df['Сумма операции'].sum()
    result_df = pd.DataFrame({'Суммарные траты': [total_spending]})
    return result_df


# if __name__ == '__main__':
#     print(spending_by_category(df, 'Супермаркеты', '31.10.2019'))
#     # print(df)
