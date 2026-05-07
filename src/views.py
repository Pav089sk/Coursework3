import datetime
import pandas as pd



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



if __name__ == '__main__':
    # print(get_day("2025-06-17 23:45:21"))
    print(excel_read('../data/operations.xlsx'))

