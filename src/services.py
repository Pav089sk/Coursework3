import re
import json
from src.views import excel_read


def find_transaction():
    """Функция поиска транзакций по телефону в формате '... +7 995 555-55-55'"""
    new_transact = {}
    operations = excel_read('../data/operations.xlsx')
    for operation in operations:
        find_param = re.findall(r'\+\d\s\d{3}\s\d{3}-\d{2}-\d{2}',operation.get('Описание', ''))
        for phone in find_param:
            new_transact[phone] = operation
        # if find_param:
        #     new_transact.append(operation)

    json_data = json.dumps(new_transact, ensure_ascii=False)

    return json_data

if __name__ == '__main__':
    print(find_transaction())
