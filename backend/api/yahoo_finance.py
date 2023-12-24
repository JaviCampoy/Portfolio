import csv
import logging
import random
from datetime import datetime
from io import StringIO
from typing import Dict, Optional, Text

import ipdb
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # NOTSET=0 < DEBUG=10 < INFO=20 < WARN=30 < ERROR=40 < CRITICAL=50

# Used for dual client <-> server communication/authentication. Avoids a "forbidden" response.


def time_formatter(input_date: Text) -> datetime:
    date_and_time = "%Y/%m/%d %H:%M:%S"
    date_only = "%Y/%m/%d"

    if "-" in input_date:
        return input_date.replace("-", "/")
        logger.info("Date formar modified so that it uses YYYY/MM/DD")
    elif "/" in input_date:
        return input_date
    else:
        raise ValueError("Please use either '-' or '/' when inserting a date")


class YStock:
    def __init__(
        self,
        ticker: Text,
        interval: Text,
        start_date: Optional[Text] = None,
        end_date: Optional[Text] = None,
        range: Optional[Text] = None,
        _events: Text = "history",
    ):
        self.ticker = ticker

        if interval not in [
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ]:
            raise ValueError
        else:
            self.interval = interval

        if start_date:
            try:
                self.start_date = datetime.strptime(time_formatter(start_date), "%Y/%m/%d %H:%M:%S")
            except ValueError:
                self.start_date = datetime.strptime(
                    time_formatter(start_date) + " 00:00:00", "%Y/%m/%d %H:%M:%S"
                )
        else:
            None

        if end_date:
            try:
                self.end_date = datetime.strptime(time_formatter(end_date), "%Y/%m/%d %H:%M:%S")
            except ValueError:
                self.end_date = datetime.strptime(
                    time_formatter(end_date) + " 23:59:59", "%Y/%m/%d %H:%M:%S"
                )
        else:
            None

        if range not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            if range == ("max" | "ytd"):
                raise ValueError("Sorry, the logic for 'max' range is not implemented yet")
            raise ValueError
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

        self.events = _events

    def _get_params(self) -> Dict:
        params = {"events": self.events, "interval": self.interval}
        if self.interval != None:
            params["interval"] = self.interval
        else:
            params["period1"] = self.start_date.timestamp()
            params["period2"] = self.end_date.timestamp()

        return params

    def _conn_api(self, conn_ticker: Text) -> pd.DataFrame:
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
            with requests.get(
                _stock_url.format(conn_ticker), params=self._get_params(), headers=header
            ) as response:
                # ipdb.set_trace()
                response.raise_for_status()
                if response.status_code == 200:
                    return response
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error while retrieving data -> {e}")
            if response.status_code == 403:
                print(f"403 - Forbidden access. User Agent was: \n{header}")
        except requests.exceptions.RequestException as e:
            print(f"Error with requests while retrievent data -> {e}")
        except Exception as e:
            print(f"There was an issue while retrieving data -> {e}")

        return pd.DataFrame

    def data_loader(self, response: requests.Response | pd.DataFrame) -> pd.DataFrame:
        conn_response = self._conn_api(self.ticker)
        logger.info("Connection to the API has been succesfully established")
        file = StringIO(conn_response.text)
        reader = csv.reader(file)
        data = list(reader)
        data_df = pd.DataFrame(pd.DataFrame(data[1:], columns=data[0]))
        return data_df
