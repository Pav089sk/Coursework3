import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import requests

from src.views import card_stat, convert, excel_read, get_day, stocks_price, top_transactions, user_settings_import
from tests.conftest import data_fixture


def test_get_day():
    """ "Тестировние функции корректного приветствия в зависимости от времени"""
    assert get_day("2025-06-17 23:45:21") == "Доброй ночи"
    assert get_day("2025-06-17 22:59:59") == "Добрый вечер"
    assert get_day("2025-06-17 17:45:21") == "Добрый день"
    assert get_day("2025-06-17 06:45:21") == "Доброе утро"


@patch("pandas.read_excel")
def test_excel_read_with_patch(mock_read_excel, data_fixture):
    """Тестирование функции открытия файла excel"""
    expected_df = pd.DataFrame(data_fixture)
    mock_read_excel.return_value = expected_df
    result = excel_read("path.xlsx")
    mock_read_excel.assert_called_once_with("path.xlsx")
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, expected_df)


def test_card_stat(data_fixture):
    """Тестирование корректного возврата данных по карте"""
    expected_df = pd.DataFrame(data_fixture)
    assert card_stat(expected_df) == [{"cashback": 0, "last_digits": "7197", "total_spent": 2620.96}]


def test_top_transact(data_fixture):
    """Тестирование корректного возврата топ-5 транзакций"""
    expected_df = pd.DataFrame(data_fixture)
    assert top_transactions(expected_df) == [
        {"amount": 3000.0, "category": "Переводы", "date": "01.01.2018", "description": "Линзомат ТЦ Юность"},
        {"amount": 1065.9, "category": "Супермаркеты", "date": "06.01.2018", "description": "Пятёрочка"},
        {"amount": 1025.0, "category": "Топливо", "date": "05.01.2018", "description": "Pskov AZS 12 K2"},
        {"amount": 316.0, "category": "Красота", "date": "04.01.2018", "description": "OOO Balid"},
        {"amount": 120.0, "category": "Цветы", "date": "07.01.2018", "description": "Magazin  Prestizh"},
    ]


def test_user_settings_import(settings_data):
    """Тестирование корректного получения информации из файла json"""
    mock_file = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", mock_file):
        result = user_settings_import("path.json")
    assert result == settings_data
    mock_file.assert_called_once_with("path.json")


def test_convert_with_mock(mock_data, api_response):
    """Тестирование корректной работы функции возврата курса валют"""
    mock_response = Mock()
    mock_response.json.return_value = api_response
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)

    expected_result = {
        "currency_rates": [
            {"currency": "USD", "rate": 74.07},
            {"currency": "EUR", "rate": 81.97},
            {"currency": "GBP", "rate": 95.24},
        ]
    }
    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_status_code(mock_data, api_response):
    """Для функции возврата курса валют тестируем некорректные статус коды"""
    mock_response = Mock()
    mock_response.json.return_value = api_response
    mock_response.status_code = 301 or 404 or 401 or 403 or 500
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)
        expected_result = {"error": f"Ошибка API: HTTP {mock_response.status_code}", "currency_rates": []}
    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_not_api_dict(mock_data, api_empty_response):
    """Тестируем работу функции возврата курса валют при пустом ответе от API"""
    mock_response = Mock()
    mock_response.json.return_value = api_empty_response
    mock_response.status_code = 200
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)
        expected_result = {"error": "Не получены данные о курсах валют от API", "currency_rates": []}
    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_incorrect_rate(mock_data, api_incorrect_rates):
    """Тестируем работу функции возврата курса валют при ответе от API с некорректными стоимостями"""
    mock_response = Mock()
    mock_response.json.return_value = api_incorrect_rates
    mock_response.status_code = 200
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)

        expected_result = {
            "currency_rates": [],
            "error": "Ошибка обработки данных: unsupported operand type(s) for /: 'int' " "and 'str'",
        }

    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_timeout(mock_data):
    """Тестируем работу функции возврата курса валют при длительном ожидании ответе от API"""
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.Timeout
    with patch("requests.get", side_effect=requests.exceptions.Timeout) as mock_get:
        result = convert(mock_data)

        expected_result = {"error": "Превышено время ожидания ответа от сервера", "currency_rates": []}

    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_connection_error(mock_data):
    """Тестируем работу функции возврата курса валют при отсутствии соединения"""
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.ConnectionError
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError) as mock_get:
        result = convert(mock_data)

        expected_result = {"error": "Ошибка подключения к серверу (проблемы с интернетом)", "currency_rates": []}

    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_except_request(mock_data):
    """Тестируем работу функции возврата курса валют при некорректном запросе к API"""
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.RequestException
    with patch("requests.get", side_effect=requests.exceptions.RequestException) as mock_get:
        result = convert(mock_data)

        expected_result = {"error": "Общая ошибка запроса: ", "currency_rates": []}

    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_other_except(mock_data):
    """Тестируем работу функции возврата курса валют при некорректых данных"""
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.RequestException
    with patch("requests.get", side_effect=(KeyError, ValueError, TypeError)) as mock_get:
        result = convert(mock_data)

        expected_result = {"error": "Ошибка обработки данных: ", "currency_rates": []}

    assert result == expected_result
    mock_get.assert_called_once_with(
        "https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10
    )


def test_stocks_price_with_mock(mock_stocks_data):
    """Тестируем работу функции возврата стоимости акций через API"""
    mock_td_client = Mock()
    mock_price_data = {"AAPL": {"price": 150.25}, "AMZN": {"price": 3200.75}, "GOOGL": {"price": 2750.50}}

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=mock_price)

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "stock_prices": [
            {"stock": "AAPL", "price": 150.25},
            {"stock": "AMZN", "price": 3200.75},
            {"stock": "GOOGL", "price": 2750.50},
        ]
    }
    assert result == expected_result
    assert mock_td_client.price.call_count == 3


def test_not_price(mock_stocks_data):
    """Тестируем работу функции возврата стоимости акций через API при отсутствии поля 'price'"""
    mock_price_data = {"AAPL": {"pr": 150.25}, "AMZN": {"pr": 3200.75}, "GOOGL": {"pr": 2750.50}}
    mock_td_client = Mock()

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=mock_price)

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "errors": [
            "Для AAPL: не найдено поле 'price' в ответе API",
            "Для AMZN: не найдено поле 'price' в ответе API",
            "Для GOOGL: не найдено поле 'price' в ответе API",
        ],
        "stock_prices": [],
    }
    assert result == expected_result


def test_for_no_price(mock_stocks_data):
    """Тестируем работу функции возврата стоимости акций через API при 'price' = None"""
    mock_price_data = {"AAPL": {"price": None}, "AMZN": {"price": 3200.75}, "GOOGL": {"price": 2750.50}}
    mock_td_client = Mock()

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=mock_price)

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "errors": ["Для AAPL: получено значение None для цены"],
        "stock_prices": [{"price": 3200.75, "stock": "AMZN"}, {"price": 2750.5, "stock": "GOOGL"}],
    }
    assert result == expected_result


def test_mistake_value(mock_stocks_data):
    """Тестируем работу функции возврата стоимости акций через API при отсутствии поля 'price'"""
    mock_price_data = {"AAPL": {"pr": 150.25}, "AMZN": {"pr": 3200.75}, "GOOGL": {"pr": 2750.50}}
    mock_td_client = Mock()

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=(ValueError, TypeError))

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "errors": [
            "Для AAPL: общая ошибка запроса — ",
            "Для AMZN: общая ошибка запроса — ",
            "Для GOOGL: общая ошибка запроса — ",
        ],
        "stock_prices": [],
    }
    assert result == expected_result


def test_incorrect_value(mock_stocks_data):
    """Тестируем работу функции возврата стоимости акций через API при некорректной цене"""
    mock_price_data = {"AAPL": {"price": "AAPL"}, "AMZN": {"price": "AMZN"}, "GOOGL": {"price": "GOOGL"}}
    mock_td_client = Mock()

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=mock_price)

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "errors": [
            "Для AAPL: ошибка преобразования цены в число — could not convert " "string to float: 'AAPL'",
            "Для AMZN: ошибка преобразования цены в число — could not convert " "string to float: 'AMZN'",
            "Для GOOGL: ошибка преобразования цены в число — could not convert " "string to float: 'GOOGL'",
        ],
        "stock_prices": [],
    }
    assert result == expected_result


def test_critical(mock_stocks_data):
    """Тестируем работу функции при ошибке инициализации или критической ошибке"""
    with patch("src.views.TDClient", side_effect=Exception("Client initialization failed")) as mock_td_client:
        result = stocks_price(mock_stocks_data)

    expected_result = {
        "error": "Критическая ошибка при работе с API: Client initialization failed",
        "errors": [],
        "stock_prices": [],
    }
    mock_td_client.assert_called_once()
    assert result == expected_result
