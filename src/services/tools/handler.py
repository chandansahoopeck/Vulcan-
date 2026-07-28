import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ToolHandler(ABC):
    """Abstract base class for tool handlers"""

    @abstractmethod
    def process_ticket(self, ticket_data):
        """Process tool-specific ticket data"""
        pass

    @abstractmethod
    def execute_automation(self, username, securitygroup, location=None):
        """Execute tool-specific automation

        `location` is optional and may be used by some handlers (e.g. SolidWorks).
        Handlers that don't need it can ignore the argument.
        """
        pass


def request_add_user_group(groupName, upn):
    print(f"\n\n Request_add_user_group for {upn} in Security Grp {groupName}\n\n")
    powershellurl = os.getenv("POWERSHELL_URL")
    url = f"{powershellurl}group/{groupName}/user/{upn}"
    print(f"\n\n***********URL TO POWERSHELL{url}\n\n************\n")
    res = requests.post(url)
    result = {"result": "failure"}
    try:
        result = res.json()
        # result={"result":"Success"}
        return result
    except Exception as err:
        logging.info(
            f"failed in processing request to managing user accounts {upn} to group {groupName} - Error: {err}"
        )


class MinitabHandler(ToolHandler):
    """Handler for New Tool License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing New Tool ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(
                f"\n\nResult from Powershell Script for MinitabHandler {username} is  {result}\n\n"
            )
            return result
        except Exception as e:
            logging.error(f"Error executing MinitabHandler automation: {str(e)}")
            return None


class BeyondCompareHandler(ToolHandler):
    """Handler for Beyond Compare License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing Beyond Compare ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(
                f"\n\nResult from Powershell Script for BeyondCompareHandler {username} is  {result}\n\n"
            )
            return result
        except Exception as e:
            logging.error(f"Error executing BeyondCompareHandler automation: {str(e)}")
            return None


class DockerHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing Docker ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(f"\n\nResult from Powershell Script for Docker {username} is  {result}\n\n")
            return result
        except Exception as e:
            logging.error(f"Error executing Docker automation: {str(e)}")
            return None


class BricsCADHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing BricsCADHandler ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(
                f"\n\nResult from Powershell Script for BricsCADHandler {username} is  {result}\n\n"
            )
            return result
        except Exception as e:
            logging.error(f"Error executing BricsCADHandler automation: {str(e)}")
            return None


class DWGTrueViewHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing DWGTrueViewHandler ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(
                f"\n\nResult from Powershell Script for DWGTrueViewHandler {username} is  {result}\n\n"
            )
            return result
        except Exception as e:
            logging.error(f"Error executing DWGTrueViewHandler automation: {str(e)}")
            return None


class SolidWorkscadHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing SolidWorkscadHandler ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation

        If `location` is provided the handler filters security groups by a location code.
        """
        try:
            if location:
                locationcode = "-" + location[:3]
                sec_grp_list = securitygroup.split(",")

                filtered_list = [item for item in sec_grp_list if locationcode in item]
                if len(filtered_list) == 1:
                    result = request_add_user_group(filtered_list[0], username)
                    print(
                        f"\n\nResult from Powershell Script for SolidWorkscadHandler {username} is  {result}\n\n"
                    )
                    return result
                else:
                    print(f"\n\n No Matching Security Found for the Location {locationcode}")
                    return "NOMATCHFOUND"
            else:
                # fall back to generic behavior if no location specified
                result = request_add_user_group(securitygroup, username)
                print(
                    f"\n\nResult from Powershell Script for SolidWorkscadHandler {username} is  {result}\n\n"
                )
                return result
        except Exception as e:
            logging.error(f"Error executing SolidWorkscadHandler automation: {str(e)}")
            return None


class Solidworkspdm(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing solidworkspdm ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(
                f"\n\nResult from Powershell Script for solidworkspdm {username} is  {result}\n\n"
            )
            return result

            # print(f"\n\nResult from Powershell Script for VisualStudioHandler {username} is  \n\n")
        except Exception as e:
            logging.error(f"Error executing solidworkspdm automation: {str(e)}")
            return None


class VSRHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing VSRHandler  ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(f"\n\nResult from Powershell Script for VSRHandler {username} is  {result}\n\n")
            return result

        except Exception as e:
            logging.error(f"Error executing VisualStudioHandler automation: {str(e)}")
            return None

class JmpHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing VSRHandler  ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(f"\n\nResult from Powershell Script for VSRHandler {username} is  {result}\n\n")
            return result

        except Exception as e:
            logging.error(f"Error executing VisualStudioHandler automation: {str(e)}")
            return None

class AnacondaHandler(ToolHandler):
    """Handler for Docker License Requests"""

    def process_ticket(self, ticket_data):
        """Process new tool-specific ticket"""
        logging.info(f"Processing VSRHandler  ticket: {ticket_data['number']}")
        # Add tool-specific logic here
        return ticket_data

    def execute_automation(self, username, securitygroup, location=None):
        """Execute new tool-specific automation"""
        try:
            result = request_add_user_group(securitygroup, username)
            print(f"\n\nResult from Powershell Script for VSRHandler {username} is  {result}\n\n")
            return result

        except Exception as e:
            logging.error(f"Error executing VisualStudioHandler automation: {str(e)}")
            return None


class HandlerFactory:
    """Factory for creating tool-specific handlers"""

    @staticmethod
    def get_handler(tool_description: str) -> ToolHandler:
        """Get handler for tool type based on description"""
        print("\n\nDescription In Handler", tool_description, "\n\n")
        handlers = {
            "minitab": MinitabHandler,
            "beyondcompare": BeyondCompareHandler,
            "docker": DockerHandler,
            "bricscad": BricsCADHandler,
            "dwgtrueview": DWGTrueViewHandler,
            "solidworks": SolidWorkscadHandler,
            "solidworkspdm": Solidworkspdm,
            "microsoftvisualstudio": VSRHandler,
            "jmp":JmpHandler,
            "anaconda":AnacondaHandler,
            # Add more tools here as needed
        }

        if tool_description is not None:
            tool_description = tool_description.replace(" ", "").lower()
        handler_class = handlers.get(tool_description)
        print(f"\nhandler_class:{handler_class}\n")
        if not handler_class:
            raise ValueError(f"Unknown tool type: {tool_description}")

        return handler_class()
