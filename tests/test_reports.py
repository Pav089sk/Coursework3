from src.reports import spending_by_category
import pandas as pd
import pytest

def test_basic_case(basic_transactions):
    result = spending_by_category(basic_transactions, 'Продукты')
    assert result['Суммарные траты'][0] == 400


def test_empty_dataframe(empty_transactions):
    result = spending_by_category(empty_transactions, 'Продукты')
    assert result['Суммарные траты'][0] == 0
