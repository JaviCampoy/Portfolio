import unittest
from unittest.mock import patch
from src.backend.app.mysql_yahoo_finance_connection import YStockMySQL
import json


class TestYStockDBConnection(unittest.TestCase):

    def read_credentials_from_json(self, json_file):
        with open(json_file, 'r') as file:
            all_credentials = json.load(file)
            mysql_credentials = all_credentials.get("mysql", {})
        return mysql_credentials.get("user"), mysql_credentials.get("password")

    @patch.object(YStockMySQL, "server_connect") # We mock the connect class method within the constructor, so that we avoid it trying to actually connect to the db
    def test_init(self, mock_server_connect):
        """
        Testing that the inheritance from the framework is OK (host) and and super for both 'user' and 'password'
        """
        mock_server_connect.return_value = True

        instance = YStockMySQL(user="test_user", password="123456")

        mock_server_connect.assert_called()
        self.assertEqual(instance.user, "test_user")
        self.assertEqual(instance.password, "123456")
        self.assertEqual(instance.host, "localhost")       

    def test_server_connect(self):
        user, password = self.read_credentials_from_json("credentials.json")
        params = {
            "user": user,
            "password": password
        }

        instance = YStockMySQL(**params)
        connection = instance.server_connect()

        self.assertEqual(connection.is_connected(), True)

        connection.close()

        self.assertEqual(connection.is_connected(), False)



