import csv
import logging
import random
from datetime import datetime
from io import StringIO
from typing import Any, Callable, Dict, Optional, Text

import ipdb
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # NOTSET=0 < DEBUG=10 < INFO=20 < WARN=30 < ERROR=40 < CRITICAL=50

# Used for dual client <-> server communication/authentication. Avoids a "forbidden" response.


def time_formatter(input_date: Text) -> Text:
    """
    This functions is a local formatter for the input dates (start and end).
    It makes sure dates are always separated by '/'. If '-' is used, it does replace it.

    Args:
        input_date (Text): Date (or date + time) in str format.

    Raises:
        ValueError: Raise an error when the date is separated by any other symbol.

    Returns:
        Text: Date in %Y/%m/%d format
    """
    if "-" in input_date:
        return input_date.replace("-", "/")
        logger.info("Date formar modified so that it uses YYYY/MM/DD")
    elif "/" in input_date:
        return input_date
    else:
        raise ValueError("Please use either '-' or '/' when inserting a date")


class YStock:
    """
    Custom class for interacting with the Yahoo Finance API, so that historical data can be downloaded.
    """

    def __init__(
        self,
        ticker: Text,
        interval: Text,
        start_date: Optional[Text] = None,
        end_date: Optional[Text] = None,
        range: Optional[Text] = None,
        _events: Text = "history",
    ):
        """
        This constructor initializes de YStock class.
        Limitations in date range along with time interval are those from the actual Yahoo Finance API.

        Arguments:
            ticker (str): Security stock ticker of your choice.
            interval (str): Desired time frequency for historical data.
            start_date (str, opcional): Starting date and time for historical data in 'YYYY/MM/DD HH:MM:SS' format. When no time is provided, 00:00:00 is used
            end_date (str, opcional): Ending date and time for historical data in 'YYYY/MM/DD HH:MM:SS' format. When no time is provided, 23:59:59 is used
            range (str, opcional): Instead of stating start and end dates, a date range is selected. It starts from 'current' going backwards up to 'range'.
            _events (str, opcional): Event type to obtain. Set to be 'history' by default.

        Raises:
            ValueError: For 'interval' if value is not included in the provided list.
            ValueError: For 'range' if value is not included in the provided list.
            ValueError: For 'range' when 'ytd' is selected (on hold).

        Returns:
            ticker (str): As per above.
            interval (str): As per above.
            start_date (datetime): As per above. if 'range' is used, the start date is considered the current one.
            end_date (datetime): As per above. if 'range' is used, the end date is considered the current one minus the 'range'.
            events (str): Tyepe of events to obtain.
        """

        self.ticker = ticker

        self.events = _events

        if interval not in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]:
            raise ValueError
        else:
            self.interval = interval

        if start_date:
            try:
                self.start_date = datetime.strptime(time_formatter(start_date), "%Y/%m/%d %H:%M:%S")
            except ValueError:
                self.start_date = datetime.strptime(time_formatter(start_date) + " 00:00:00", "%Y/%m/%d %H:%M:%S")
        else:
            None

        if end_date:
            try:
                self.end_date = datetime.strptime(time_formatter(end_date), "%Y/%m/%d %H:%M:%S")
            except ValueError:
                self.end_date = datetime.strptime(time_formatter(end_date) + " 23:59:59", "%Y/%m/%d %H:%M:%S")
        else:
            None

        if range:
            if range not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
                raise ValueError
            elif range == "max" or range == "ytd":
                raise ValueError("Sorry, the logic for 'max' range is not implemented yet")
            else:
                self.end_date = datetime.now()
                if "d" in range:
                    value = int(range.split("d")[0])
                    self.start_date = self.end_date - relativedelta(days=value)
                elif "mo" in range:
                    value = int(range.split("mo")[0])
                    self.start_date = self.end_date - relativedelta(months=value)
                else:
                    value = int(range.split("y")[0])
                    self.start_date = self.end_date - relativedelta(years=value)
        else:
            return None

    def _get_params(self) -> Dict:
        """
        Gathers the used params for the request (private)

        Returns:
            Dict: A dictionary containing all the params
        """

        params = {
            "ticker": self.ticker,
            "interval": self.interval,
            "period1": int(self.start_date.timestamp()),
            "period2": int(self.end_date.timestamp()),
            "events": self.events,
        }
        return params

    @property
    def get_params(self) -> Callable[[], dict[Any, Any]]:
        """
        A getter for the all the private params

        Returns:
            Callable[[], dict[Any, Any]]: Calls the _get_params method and return the params out of the class
        """

        return self._get_params

    def _conn_api(self) -> requests.Response:
        """
        Creates the connection to the API Yahoo Finance and returns its respons

        Raises:
            http_ex: Catches exceptions HTTP related exceptions
            request_ex: Catches exceptions request related
            ex: Catches any other exception
            RuntimeError: reutrn type for non-succesful requests that are not catched (mainly for Mypy clean up signals)

        Returns:
            requests.Response: _description_
        """

        _HEADERS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
        ]

        _stock_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?"

        try:
            header = {"User-Agent": "{}".format(random.choice(_HEADERS))}
            logger.debug("Selected header -> {}".format(header))
            with requests.get(_stock_url.format(self.ticker), params=self._get_params(), headers=header) as response:
                # ipdb.set_trace()
                response.raise_for_status()
                if response.status_code == 200:
                    return response
        except requests.exceptions.HTTPError as http_ex:
            print(f"**** HTTP error while retrieving data ****  \n---> {http_ex} \n---> {response.text}")
            if response.status_code == 403:
                print(f"**** 403 - Forbidden access **** \n---> User Agent was: \n---> {header}")
            raise http_ex
        except requests.exceptions.RequestException as request_ex:
            print(f"**** Error with requests while retrievent data **** \n ---> {request_ex} \n---> {response.text}")
            raise request_ex
        except Exception as ex:
            print(f"**** There was an issue while retrieving data **** \n ---> {ex} \n---> {response.text}")
            raise ex

        raise RuntimeError("Unexpected flow reached in _conn_api")

    @property
    def get_response(self):
        """
        Returns the status code from the API request

        Returns:
            int: API response status code
        """
        return self._conn_api().status_code

    def data_loader(self) -> pd.DataFrame:
        """
        Loads the historical data from the response and creates a Pandas Dataframe containing it

        Returns:
            pd.DataFrame: Historical data (instances)
        """

        conn_response = self._conn_api()
        logger.info("Connection to the API has been succesfully established")
        file = StringIO(str(conn_response.text))
        reader = csv.reader(file)
        data = list(reader)
        data_df = pd.DataFrame(pd.DataFrame(data[1:], columns=data[0]))
        return data_df
