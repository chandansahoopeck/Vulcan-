import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure/Office 365 Configuration
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
username = os.getenv("AZURE_USERNAME")
password = os.getenv("AZURE_PASSWORD")
grant_type = "password"
tenant_id = os.getenv("AZURE_TENANT_ID")
USER = os.getenv("AZURE_USERNAME")
shared_mailbox = os.getenv("SHARED_MAILBOX")

scope = [os.getenv("GRAPH_SCOPE")]
token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
graph_endpoint = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/sendMail"

# Parse recipients from comma-separated string
recipients_str = os.getenv("EMAIL_RECIPIENTS", "")
recipients = [email.strip() for email in recipients_str.split(",") if email.strip()]

bccrecipients_str = os.getenv("EMAIL_BCC_RECIPIENTS", "")
bccrecipients = [email.strip() for email in bccrecipients_str.split(",") if email.strip()]

mailbox = os.getenv("MAILBOX")
template = {
    "notify_approvers": os.getenv("EMAIL_TEMPLATE_NOTIFY_APPROVERS"),
    "test": os.getenv("EMAIL_TEMPLATE_TEST"),
}
smtp_hostname = os.getenv("SMTP_HOSTNAME")
smtp_port = int(os.getenv("SMTP_PORT", 587))
images = {
    "image1": {"path": os.getenv("IMAGE_WD_BLACK_PATH"), "tag": os.getenv("IMAGE_WD_BLACK_TAG")},
}

body = {
    "client_id": client_id,
    "client_secret": client_secret,
    "username": username,
    "password": password,
    "grant_type": "password",
    "scope": " ".join(scope),
}
