from backend.api.yahoo_finance import YStock

if __name__ == "__main__":
    df = YStock(
        ticker="AAPL", interval="1d", start_date="2023/10/03 13:34:16", end_date="2023/12/03 13:34:16"
    ).data_loader()
