import json
from unittest.mock import Mock, mock_open, patch
import pandas as pd
from src.views import card_stat, convert, excel_read, get_day, stocks_price, top_transactions, user_settings_import
from tests.conftest import data_fixture
import requests


def test_get_day():
    assert get_day("2025-06-17 23:45:21") == "Доброй ночи"
    assert get_day("2025-06-17 22:59:59") == "Добрый вечер"
    assert get_day("2025-06-17 17:45:21") == "Добрый день"
    assert get_day("2025-06-17 06:45:21") == "Доброе утро"


@patch("pandas.read_excel")
def test_excel_read_with_patch(mock_read_excel, data_fixture):
    expected_df = pd.DataFrame(data_fixture)
    mock_read_excel.return_value = expected_df
    result = excel_read("path.xlsx")
    mock_read_excel.assert_called_once_with("path.xlsx")
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, expected_df)


def test_card_stat(data_fixture):
    expected_df = pd.DataFrame(data_fixture)
    assert card_stat(expected_df) == [{"cashback": 0, "last_digits": "7197", "total_spent": 2620.96}]


def test_top_transact(data_fixture):
    expected_df = pd.DataFrame(data_fixture)
    assert top_transactions(expected_df) == [
            {"amount": 3000.0, "category": "Переводы", "date": "01.01.2018", "description": "Линзомат ТЦ Юность"},
            {"amount": 1065.9, "category": "Супермаркеты", "date": "06.01.2018", "description": "Пятёрочка"},
            {"amount": 1025.0, "category": "Топливо", "date": "05.01.2018", "description": "Pskov AZS 12 K2"},
            {"amount": 316.0, "category": "Красота", "date": "04.01.2018", "description": "OOO Balid"},
            {"amount": 120.0, "category": "Цветы", "date": "07.01.2018", "description": "Magazin  Prestizh"},
        ]


def test_user_settings_import(settings_data):
    mock_file = mock_open(read_data=json.dumps(settings_data))
    with patch("builtins.open", mock_file):
        result = user_settings_import("path.json")
    assert result == settings_data
    mock_file.assert_called_once_with("path.json")


def test_convert_with_mock(mock_data, api_response):
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
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB", timeout=10)

def test_status_code(mock_data, api_response):
    mock_response = Mock()
    mock_response.json.return_value = api_response
    mock_response.status_code = 301 or 404 or 401 or 403 or 500
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)
        expected_result = {
                "error": f"Ошибка API: HTTP {mock_response.status_code}",
                "currency_rates": []
            }
    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                     timeout=10)

def test_not_api_dict(mock_data, api_empty_response):
    mock_response = Mock()
    mock_response.json.return_value = api_empty_response
    mock_response.status_code = 200
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)
        expected_result = {
                "error": "Не получены данные о курсах валют от API",
                "currency_rates": []
            }
    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)

def test_uncorrect_rate(mock_data,api_uncorrect_rates):
    mock_response = Mock()
    mock_response.json.return_value = api_uncorrect_rates
    mock_response.status_code = 200
    with patch("requests.get", return_value=mock_response, timeout=10) as mock_get:
        result = convert(mock_data)

        expected_result = {'currency_rates': []}

    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)

def test_timeout(mock_data):
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.Timeout
    with patch("requests.get", side_effect=requests.exceptions.Timeout) as mock_get:
        result = convert(mock_data)

        expected_result = {
            "error": "Превышено время ожидания ответа от сервера",
            "currency_rates": []
        }

    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)

def test_connection_error(mock_data):
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.ConnectionError
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError) as mock_get:
        result = convert(mock_data)

        expected_result = {
            "error": "Ошибка подключения к серверу (проблемы с интернетом)",
            "currency_rates": []
        }

    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)

def test_except_request(mock_data):
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.RequestException
    with patch("requests.get", side_effect=requests.exceptions.RequestException) as mock_get:
        result = convert(mock_data)

        expected_result ={
            "error": f"Общая ошибка запроса: ",
            "currency_rates": []
        }

    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)


def test_other_except(mock_data):
    mock_response = Mock()
    mock_response.json.return_value = requests.exceptions.RequestException
    with patch("requests.get", side_effect=(KeyError, ValueError, TypeError)) as mock_get:
        result = convert(mock_data)

        expected_result = {
        "error": f"Ошибка обработки данных: ",
        "currency_rates": []
        }

    assert result == expected_result
    mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/629ef18b30f0f590cca623f8/latest/RUB",
                                         timeout=10)

def test_stocks_price_with_mock(mock_stocks_data):
    mock_td_client = Mock()
    mock_price_data = {"AAPL": {"price": 150.25}, "AMZN": {"price": 3200.75}, "GOOGL": {"price": 2750.50}}

    def mock_price(symbol):
        mock_result = Mock()
        mock_result.as_json.return_value = mock_price_data.get(symbol, {})
        return mock_result

    mock_td_client.price = Mock(side_effect=mock_price)

    with patch("src.views.TDClient", return_value=mock_td_client):
        result = stocks_price(mock_stocks_data)
    parsed_result = json.loads(result)
    expected_result = {
        "stock_prices": [
            {"stock": "AAPL", "price": 150.25},
            {"stock": "AMZN", "price": 3200.75},
            {"stock": "GOOGL", "price": 2750.50},
        ]
    }
    assert parsed_result == expected_result
    assert mock_td_client.price.call_count == 3
