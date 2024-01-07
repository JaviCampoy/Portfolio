import unittest
from src.backend.app.mysql_yahoo_finance_connection import YStockMySQL

class TestYStockDBConnection(unittest.TestCase):
    def test_connect(self):
        """
        Testing that the inheritance from the framework is OK (host) and and super for both 'user' and 'password'
        """
        instance = YStockMySQL(user="test_user", password="123456")
        self.assertEqual(instance.user, "test_user")
        self.assertEqual(instance.password, "123456")
        self.assertEqual(instance.host, "localhost")
