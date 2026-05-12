import json

from src.views import card_stat, convert, excel_read, get_day, stocks_price, top_transactions, user_settings_import


def main_function(input_datetime: str) -> str:
    greeting = get_day(input_datetime)
    operations = excel_read("data/operations.xlsx")
    cards = card_stat(operations)
    top_trans = top_transactions(operations)

    user_settings = user_settings_import("user_settings.json")

    currency_rates_data = convert(user_settings)
    currency_rates = currency_rates_data["currency_rates"]  # теперь это список, берём напрямую

    stock_prices_data = stocks_price(user_settings)
    stock_prices = stock_prices_data["stock_prices"]  # теперь это список, берём напрямую

    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_trans,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print(main_function("2020-06-17 23:45:21"))
