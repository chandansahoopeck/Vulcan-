import json
import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

from src.services.cyberark.cyberark import cyberark

# Load environment variables from .env file
load_dotenv()


class ODBC(ABC):
    def __init__(self) -> None:
        self.url = os.getenv("SERVICENOW_ODBC_URL")
        self.url_query = os.getenv("SERVICENOW_ODBC_URL")
        self.headers = {
            "Authorization": os.getenv("SERVICENOW_ODBC_AUTH_HEADER"),
            "Content-Type": "application/json",
        }
        self.__set_pwd()

    def __set_pwd(self):
        cb = cyberark("RPA_Tool")
        pwd = cb.get_cyberark_object()
        self.pwd = pwd["password"]

    @abstractmethod
    def run(self):
        pass


class GenericOdbc(ODBC):
    def __init__(self, tool_descriptions: list = None):
        super().__init__()
        self.tool_descriptions = tool_descriptions or [
            "- Beyond Compare",
            "- SolidWorks",
            "- Minitab",
            "- BricsCAD",
            "- Docker",
            "- DWG TrueView",
            "- SolidWorks PDM",
            "- Anaconda",
            "- JMP",
            "- Microsoft Visual Studio"
        ]

    def run(self):
        """
        Query tasks for all configured tools from ServiceNow.
        """
        # Create OR conditions for all tool types
        # conditions = " OR ".join(
        #     [f"t.short_description like '{desc}'" for desc in self.tool_descriptions]
        # )

        sqlstatement = f""" SELECT t.dv_cat_item,t.dv_cmdb_ci,t.number,t.description,t.short_description,t.dv_u_requested_by,t.dv_u_requested_for,t.dv_location,u.email FROM sc_task t LEFT JOIN sys_user u ON t.dv_u_requested_for = u.name  WHERE t.active=1 AND  u.user_name <> '' AND  ((t.dv_cat_item ='Install/ Remove Software' and t.dv_cmdb_ci='SolidWorks PDM') or (dv_cat_item='Visual Studio Request' and  t.dv_cmdb_ci='Microsoft Visual Studio') or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='Docker') or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='BricsCAD')  or(dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='Beyond Compare')  or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='Minitab')  or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='DWG TrueView')  or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='SolidWorks') or (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='JMP') OR (dv_cat_item='Install/ Remove Software' and  t.dv_cmdb_ci='Anaconda')) AND t.dv_assignment_group like '%IT-Infra-RPA-Ops%'"""
        #AND t.active=1 AND  t.dv_u_initial_assignment_group like '%IT-Infra-RPA-Ops%'  
        #print("SQL STATMENT", sqlstatement)
        data = json.dumps(
            {
                "sqlstatement": sqlstatement,
                "uid": "RPA_Tool",
                "pwd": self.pwd,
                "url": os.getenv("SERVICENOW_BASE_URL"),
            }
        )
        resp = requests.post(url=self.url, headers=self.headers, data=data)

        
        print("HTTP:", resp.status_code)
        print("RAW:", resp.text[:2000])   # important

        resp.raise_for_status()           # throws for 4xx/5xx

        try:
            resp_json = resp.json()
            print("Tickets:", str(resp.json()))
        except ValueError:
            raise RuntimeError(f"Non-JSON response: {resp.text[:2000]}")    
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response status code: {resp.status_code}")
            print(f"Response text: {resp.text}")
          
            # Return a mock response with empty result for error cases
            class MockResponse:
                def json(self):
                    return {
                        "result": [],
                        "status": "error",
                        "message": "Failed to parse JSON response",
                    }

            return MockResponse()
  
        return resp

