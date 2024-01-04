import pandas as pd

from common.api_dataframe_processor import ApiDataProcessor


class YStockProcessor(ApiDataProcessor):
    """
    This class is based on the api_dataframe_processor framework

    Args:
        api_dataframe_processor (_type_): _description_
    """

    def __init__(self):
        pass

    @classmethod
    def column_type_modifier(cls, raw_data: pd.DataFrame) -> pd.DataFrame:
        raw_data["Open"] = raw_data["Open"].astype("float64")
        raw_data["High"] = raw_data["High"].astype("float64")
        raw_data["Low"] = raw_data["Low"].astype("float64")
        raw_data["Close"] = raw_data["Close"].astype("float64")
        raw_data["Adj Close"] = raw_data["Adj Close"].astype("float64")
        raw_data["Volume"] = raw_data["Volume"].astype("int64")

        return raw_data
