import csv
import random
from io import StringIO
from typing import Text

import pandas as pd
import requests

# Used for client <-> server communication/authentication. Avoids a "forbidden" response.
HEADERS = [
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


def get_stock_data(stock: Text) -> pd.DataFrame:
    stock_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?"

    params = {'range': '5y', 'interval': '1d', 'events': 'history'}

    try:
        header = {"User-Agent": "{}".format(random.choice(HEADERS))}
        response = requests.get(stock_url.format(stock), params=params, headers=header)
        if response.status_code == 200:
            file = StringIO(response.text)
            reader = csv.reader(file)
            data = list(reader)
            data_df = pd.DataFrame(pd.DataFrame(data[1:], columns=data[0]))
            return data_df
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error while retrieving data -> {e}")
        if response.status_code == 403:
            print(f"403 - Forbidden access. User Agent was: \n{header}")
    except requests.exceptions.RequestException as e:
        print(f"Error with requests while retrievent data -> {e}")
    except Exception as e:
        print(f"There was an issue while retrieving data -> {e}")

    return pd.DataFrame()


stock_data = get_stock_data("AAPL")
