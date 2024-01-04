from abc import ABC, abstractmethod

import pandas as pd


class ApiDataProcessor(ABC):
    """
    This is an abstract class mean to act as a framework for the data obtained through the appi data extractor.
    It modiefies whatever it is needed in this 'raw data'
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def column_type_modifier(cls, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        This mehtod aims to modify the type of data of the columns

        Returns:
            pd.DataFrame: original pd.DataFrame with new column types for existing columns
        """
        pass
