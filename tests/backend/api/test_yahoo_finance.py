import json
import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd
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
    """
    Test the time_formatter function with different input formats.

    Args:
        input_date (_type_): The input date string to be formatted.
        expected_result (_type_): The expected result after formatting.

    Raises:
        ValueError: If the input date has any other symbol that is not '/' or '-'

    Test Cases:
        - Test with date in 'YYYY/MM/DD' format.
        - Test with date in 'YYYY-MM-DD' format.
        - Test with an invalid date format, expecting a ValueError.
    """

    if "/" in input_date or "-" in input_date:
        result = time_formatter(input_date)
        assert result == expected_result
    else:
        with pytest.raises(ValueError, match="Please use either '-' or '/' when inserting a date"):
            time_formatter(input_date)


#### YStock class ####


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
    """
    Test the __init__ magic method (constructor) of the YStock class with various parameters.

    Args:
        parameters (dict): A dictionary containing parameters for creating YStock instances.

    Test Cases:
        - Test start and end dates without times.
        - Test start and end dates with times.
    """

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
        """
        Test the __init__ method of the YStock class when using range.
        """

        instance = YStock(ticker="AAPL", interval="1m", range="5d")
        self.assertAlmostEqual(
            instance.start_date,
            datetime.now() - relativedelta(days=5),
            delta=2,
            msg="Time difference went over the delta",
        )
        self.assertAlmostEqual(instance.end_date, datetime.now(), delta=2, msg="Time difference went over the delta")

    @patch("backend.api.yahoo_finance.YStock", autospec=True)
    def test_get_params(self, mock_ystock):
        """
        Test the get_params method of the YStock class using a mocked instance and real instance. Comparing them afterwards
        """

        mock_instance = mock_ystock.return_value
        mock_instance.get_params.return_value = {
            "ticker": "AAPL",
            "interval": "1m",
            "period1": 1696332856,
            "period2": 1701606856,
            "events": "history",
        }

        expected = mock_instance.get_params.return_value

        real_instance = YStock(
            ticker="AAPL", interval="1m", start_date="2023/10/03 13:34:16", end_date="2023/12/03 13:34:16"
        )

        result = real_instance.get_params()

        self.assertEqual(result["ticker"], expected["ticker"])
        self.assertEqual(result["interval"], expected["interval"])
        self.assertEqual(result["period1"], expected["period1"])
        self.assertEqual(result["period2"], expected["period2"])
        self.assertEqual(result["events"], expected["events"])

    def test_conn_api(self):
        """
        Test the conn_api method of the YStock class.
        Depending on the selected dates, the interval may fail (this is a natural behaviour from Yahoo Finance)
        """

        instance = YStock(
            ticker="AAPL", interval="1d", start_date="2023/10/03 13:34:16", end_date="2023/10/06 13:34:16"
        )
        self.assertEqual(instance.get_response, 200)

    def test_data_loader(self):
        """
        Test the data_loader method of the YStock class by means of checking the return output.
        """
        instance = YStock(
            ticker="AAPL", interval="1d", start_date="2023/10/03 13:34:16", end_date="2023/10/06 13:34:16"
        )
        result = instance.data_loader()
        self.assertEqual(type(result), pd.DataFrame)
