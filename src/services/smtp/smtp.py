import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.services.cyberark.cyberark import cyberark
from src.services.smtp.email import Email

# Load environment variables from .env file
load_dotenv()


class Smtp:
    """Send emails using WD internal template"""

    def __init__(self) -> None:
        self.username = os.getenv("SMTP_USERNAME")
        self.__get_pwd()
        self.server = os.getenv("SMTP_HOSTNAME")
        self.port = int(os.getenv("SMTP_PORT", 587))

    def __get_pwd(self):
        """Retrieve password from cyberark."""
        cb = cyberark(self.username)
        auth = cb.get_cyberark_object()
        self.__pwd = auth["password"]

    def send(self, email: Email):
        """Sends an email using SMTP"""
        msgRoot = MIMEMultipart("related")
        msgRoot["Subject"] = email.subject
        msgRoot["From"] = self.username
        msgRoot["To"] = email.to
        msgRoot.preamble = "RPA"
        msgAlternative = MIMEMultipart("alternative")
        msgRoot.attach(msgAlternative)
        msgText = MIMEText("RPA")
        msgAlternative.attach(msgText)
        # We reference the image in the IMG SRC attribute by the ID we give it below
        msgText = MIMEText(email.body, "html")

        # embed images to the email body
        msgAlternative.attach(msgText)
        for img in email.images:
            fp = open(img["path"], "rb")
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header("Content-ID", img["id"])
            msgRoot.attach(msg_img)

        # login to smtp server and sen email
        try:
            smtp = smtplib.SMTP(self.server, port=self.port, timeout=30)
            smtp.starttls()
            smtp.login(self.username, self.__pwd)
            smtp.sendmail(self.username, email.recipients, msgRoot.as_string())
            smtp.quit()
            return {"success": True, "msg": "sent"}
        except Exception as e:
            return {"success": False, "msg": str(e)}
