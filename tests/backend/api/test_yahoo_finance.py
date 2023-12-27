import json
import unittest
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from backend.api.yahoo_finance import YStock, time_formatter


#### time_formatter ####
@pytest.mark.parametrize(
    "input_date, expected_result",
    [
        ("2023/12/03", "2023/12/03"),
        ("2023-12-03", "2023/12/03"),
        ("2023.12.03", ValueError),
    ],
)
def test_time_formatter(input_date, expected_result):
    if "/" in input_date or "-" in input_date:
        result = time_formatter(input_date)
        assert result == expected_result
    else:
        with pytest.raises(ValueError, match="Please use either '-' or '/' when inserting a date"):
            time_formatter(input_date)


#### YStock ####


# YStock class parametric to test for __init__
@pytest.mark.parametrize(
    "parameters",
    [
        (
            {
                "ticker": "AAPL",
                "interval": "1m",
                "start_date": "2023-05-11",
                "end_date": "2023-07-22",
                "expected_start_date": datetime(2023, 5, 11, 0, 0),
                "expected_end_date": datetime(2023, 7, 22, 23, 59, 59),
            }
        ),
        (
            {
                "ticker": "AAPL",
                "interval": "1m",
                "start_date": "2023-05-11 14:35:21",
                "end_date": "2023-07-22 19:10:38",
                "expected_start_date": datetime(2023, 5, 11, 14, 35, 21),
                "expected_end_date": datetime(2023, 7, 22, 19, 10, 38),
            }
        ),
    ],
)
def test_init(parameters):
    instance = YStock(
        parameters["ticker"],
        parameters["interval"],
        parameters["start_date"],
        parameters["end_date"],
    )
    assert instance.start_date == parameters["expected_start_date"]
    assert instance.end_date == parameters["expected_end_date"]


class TestYStock(unittest.TestCase):
    def test_init_range(self):
        instance = YStock(ticker="AAPL", interval="1m", range="5d")
        self.assertEqual(instance.start_date, datetime.now() - relativedelta(days=5))
        self.assertEqual(instance.end_date, datetime.now())
