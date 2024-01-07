import pandas as pd
import pytest

from src.backend.api.yahoo_finance_processor import YStockProcessor

# This is some kind of mock dataframe similar to what we obtain from yahoo finance when using the 'yahoo_finance.py'
dummy_data = {
    "Date": ["2023-10-03", "2023-10-04"],
    "Open": ["172.259995", "171.089996"],
    "High": ["173.630005", "174.210007"],
    "Low": ["170.820007", "170.970001"],
    "Close": ["172.399994", "173.660004"],
    "Adj Close": ["172.173172", "173.431519"],
    "Volume": ["49594600", "53020300"],
}
dummy_df = pd.DataFrame(data=dummy_data, dtype='O')

# These are the expected column dtypes
expected_data_types = {
    "Date": 'object',
    "Open": 'float64',
    "High": 'float64',
    "Low": 'float64',
    "Close": 'float64',
    "Adj Close": 'float64',
    "Volume": 'int64',
}


@pytest.mark.parametrize("column_name, expected_column_dtype", expected_data_types.items())
def test_column_type_modifier(column_name, expected_column_dtype):
    """
    Testing the dtype modification on some columns of an input pd.DataFrame

    Args:
        column_name (str):  dataframe column name
        expected_column_dtype (str): expected dataframe column type once modified
    """
    modified_data = YStockProcessor.column_type_modifier(dummy_df)
    assert modified_data[column_name].dtype == expected_column_dtype
