import json

import pytest


def test_user_agent():
    pass


def test_ticker():
    data = '{"a": 1}'
    loaded_data = json.loads(data)
    assert isinstance(loaded_data, dict)
