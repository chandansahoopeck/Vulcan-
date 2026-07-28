import base64
import io
import re
import smtplib
from datetime import datetime, timedelta

# from src.config.ews import *
from email import *
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

import imageio
import requests
from bs4 import BeautifulSoup

from src.services.config.smtp_globals import *
from src.services.cyberark.cyberark import cyberark


class SMTP:

    def authenticate(self):
        # Define the request body

        # Make the request
        response = requests.post(token_endpoint, data=body)
        if response.status_code == 200:
            result = response.json()
            if "access_token" in result:
                return result["access_token"]
            else:
                raise Exception("Authentication failed")
        else:
            raise Exception(f"Token acquisition failed: {response.text}")

    def __embed_image(self, image_cid, image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        image_data_base64 = base64.b64encode(image_data).decode("utf-8")
        # return f'<img src="data:image/png;base64,{image_data_base64}" cid="{image_cid}">'
        style = f"max-width: 100%; height: auto; width: auto;"
        img_tag = f'<img src="data:image/png;base64,{image_data_base64}" cid="{image_cid}" style="display: block; max-width: 100%; height: auto; width: auto;">'
        return img_tag

    def sendmail(self, subject, ticket_number, short_des, status):
        html_string = ""
        with open(template["notify_approvers"], "r") as f:
            html_string = f.read()
            html_string = html_string.replace("<task>", ticket_number)
            html_string = html_string.replace("<server>", short_des)
            html_string = html_string.replace("<status>", status)
        return html_string

    def failmail(self, subject, ticket_number, short_des, status, men_user, HOST_NAME):
        html_string = ""
        with open(template["test"], "r") as f:
            html_string = f.read()
            html_string = html_string.replace("<SNOW_Request_Number>", ticket_number)
            html_string = html_string.replace("<server_name>", HOST_NAME)
            html_string = html_string.replace("<failure_reason>", short_des)
            html_string = html_string.replace("<User>", men_user)
        return html_string

    def notify_approvers_imc_got_approved(
        self, subject, ticket_number, short_des, status, usermails, men_user, HOST_NAME
    ):
        print(subject, ticket_number, short_des, status, men_user)
        # try:
        if status == "Failed":
            print("**************************")
            print(
                "subject" + subject,
                "ticket_number" + ticket_number,
                "short_des" + short_des,
                "status" + status,
                "men_user" + men_user,
                HOST_NAME,
            )
            print("**************************")
            html_string = self.failmail(
                subject, ticket_number, short_des, status, men_user, HOST_NAME
            )
        else:
            html_string = self.sendmail(
                subject,
                ticket_number,
                short_des,
                status,
            )
        access_token = self.authenticate()
        # print(access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # recipients = recipients + usermails
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_string,  # Use the html_string instead of body here
                },
                "toRecipients": [
                    {"emailAddress": {"address": recipient}} for recipient in recipients
                ],
            },
            "saveToSentItems": "true",
        }

        response = requests.post(graph_endpoint, headers=headers, json=payload)
        print(response)
        if response.status_code == 202:
            # Email sent successfully
            print("Email sent successfully")
        else:
            # Error sending email
            print("Error sending email")

    # except Exception as e:
    #     # Exception occurred
    #     print(f"Exception: {str(e)}")
