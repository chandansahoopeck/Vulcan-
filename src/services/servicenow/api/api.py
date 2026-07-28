import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from src.services.cyberark.cyberark import cyberark

# Load environment variables from .env file
load_dotenv()


class Api(ABC):
    def __init__(self) -> None:
        self.url = os.getenv("SERVICENOW_TEST_URL")
        self.headers = {
            "Accept": "Application/json",
            "Content-Type": "Application/json",
            "authorization": self.__set_pwd(),
        }

    def __set_pwd(self):
        """Get Servicenow Authentication from CyberArk Vault"""
        cb = cyberark("RPA_Tool")
        pwd = cb.get_cyberark_object()
        return pwd["basic auth"]

    @abstractmethod
    def run(self, data):
        pass
