import csv
import os
from datetime import datetime

# File name
EMAIL_LOG_FILE = "email_success_log.csv"

# Create file with headers if it doesn't exist
def initialize_email_log():
    if not os.path.exists(EMAIL_LOG_FILE):
        with open(EMAIL_LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Email_Subject", "Timestamp"])


# Function to log successful email processing
def log_email_success(subject):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(EMAIL_LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([subject, timestamp])

    print(f"Logged email: {subject}")


# Example usage
if __name__ == "__main__":
    initialize_email_log()

    # Example: emails processed successfully
    #log_email_success("Copilot License Request Approved")
    #log_email_success("Password Reset Confirmation")
