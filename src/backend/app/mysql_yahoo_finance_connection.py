from src.utilities.custom_decorators import override_params
from src.utilities.mysql_connection_framework import DbConn
from mysql.connector import connect, Error, MySQLConnection, errorcode
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

class YStockMySQL(DbConn):
    """
    This class allows the user to connect easily to MySQL

    Args:
        DbConn: Framework from which inheritance happens
    """

    def __init__(self, user, password, host=None):
        if host==None:
            super().__init__(user, password)
        else:
            super().__init__(user, password, host)

        self.connect()

    #TODO Consider using the built-in library getpass (e.g. "getpass('Enter Password: ')") so that credentials are not hard-coded
    def connect(self, attempts:int=3, delay:int=2)-> Optional[MySQLConnection]:
        """
        This class method will be executed directly once YStockMySQL gets instantiated.
        Based on the parameters from the init constructor, a connect attempt will be carried out

        Args:
            attempts (int, optiaonal): Number of connection attempts to be performed. Defaults to 3.
            delay (int, optional): Time delay between attempts. Defaults to 2 (although it will exponentiated)

        Returns:
            Optional[MySQLConnection]: Returns a connection if succesfull or None otherwise.
        """
        attempt = 1
        while attempt <= attempts + 1:
            try:
                with connect(host= self.host, user=self.user, password=self.password) as conn:
                    logger.info(f"Connection to MySQL succesfully established: \n--->{conn}")
            except Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logger.info(f"Something is wrong with your user name or password: \n--->{err}")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    logger.info("Database does not exist: \n--->{err}")
                else:
                    if attempts is attempt:
                        logger.info(f"Failed to connect. Exiting without a connection: \n--->{err}")
                        return None
                    else:
                        logger.info(f"Connection failed: \n--->{err}  \nRetrying...({attempt}/{attempts-1})")
                        time.sleep(delay**attempt)
                        attempt += 1
        return None
