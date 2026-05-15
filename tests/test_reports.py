from src.reports import param_deco, spending_by_category


def test_basic_case(basic_transactions):
    result = spending_by_category(basic_transactions, "Продукты")
    assert result["Суммарные траты"][0] == 400


def test_empty_dataframe(empty_transactions):
    result = spending_by_category(empty_transactions, "Продукты", "31.12.2021")
    assert result["Суммарные траты"][0] == 0


def test_invalid_dates(invalid_data):
    result = spending_by_category(invalid_data, "Продукты")
    assert result["Суммарные траты"][0] == 1243


def test_deco(tmp_path):
    file = tmp_path / "test.txt"

    @param_deco(file)
    def test_func(a, b):
        result = a + b
        return f"Результат работы тестовой функции {result}"

    test_func(2, 2)

    assert (
        file.read_text(encoding="utf-8")
    ) == '{\n  "result": "Результат работы тестовой функции 4",\n  "type": "str"\n}'
