import base64
import os
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import imageio
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class smtpp:
    def __init__(self, body, subject, recipients) -> None:
        self.__body = body
        self.__subject = subject
        self.__recipients = recipients
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.username = os.getenv("AZURE_USERNAME")
        self.password = os.getenv("AZURE_PASSWORD")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.scope = [os.getenv("GRAPH_SCOPE")]
        self.shared_mailbox = os.getenv("SHARED_MAILBOX")
        self.token_endpoint = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        self.graph_endpoint = (
            f"https://graph.microsoft.com/v1.0/users/{self.shared_mailbox}/sendMail"
        )
        # self.htmlfilelocation = self.__cfg.data['checkmk']['html_file_location']

    def authenticate(self):
        # Define the request body
        body = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "scope": " ".join(self.scope),
        }
        # Make the request
        response = requests.post(self.token_endpoint, data=body)
        if response.status_code == 200:
            result = response.json()
            if "access_token" in result:
                return result["access_token"]
            else:
                raise Exception("Authentication failed")
        else:
            raise Exception(f"Token acquisition failed: {response.text}")

    def __convert_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def __embed_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        image_data_base64 = base64.b64encode(image_data).decode("utf-8")
        return f'<img src="data:image/png;base64,{image_data_base64}">'

    def __read_template(self, template1):
        template = template1
        return template

    def send(self):
        try:
            access_token = self.authenticate()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            strTo = ";".join(self.__recipients)

            template = self.__read_template(self.__body)

            payload = {
                "message": {
                    "subject": self.__subject,
                    "body": {"contentType": "HTML", "content": template},
                    "toRecipients": [
                        {"emailAddress": {"address": recipient}} for recipient in self.__recipients
                    ],
                    "from": {"emailAddress": {"address": self.shared_mailbox}},
                },
                "saveToSentItems": "true",
            }

            response = requests.post(self.graph_endpoint, headers=headers, json=payload)

            if response.status_code == 202:
                # Email sent successfully
                print("Email sent successfully")
            else:
                # Error sending email
                print("Error sending email")

        except Exception as e:
            # Exception occurred
            print(f"Exception: {str(e)}")


obj = smtpp("test", "test_mail", ["hari.tupakula1@sandisk.com"])
obj.send()
