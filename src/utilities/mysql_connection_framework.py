from abc import ABC, abstractmethod
from typing import Text


class DbConn(ABC):
    """
    This class acts a framework for creating any DB connection to different database manager
    """
    def __init__(self, user:Text, password:Text, host:Text="localhost"):
        self.user = user
        self.password = password
        self.host = host

        self.connect()

    @abstractmethod
    def connect(self):
        """
        This method should be called directly once the class is instantiated.
        This creates the connection to the seleted database manager
        """
        pass 

    def create_db(self):
        """
        This method creates the database within the database manager
        """
        pass

    def create_table(self):
        """
        This creates the table in the selected database
        """
        pass

    def alter_table(self):
        """
        This modifies the selected table
        """
        pass

    def drop_table(self):
        """
        This erases the selected table
        """
        pass
