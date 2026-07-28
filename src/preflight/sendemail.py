import os
import requests
import json
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

class GraphMailer:
    """
    Sends email via Microsoft Graph sendMail API.
    Matches your reference pattern:
      - access_token = self.authenticate()
      - headers = Bearer token
      - POST graph_endpoint with payload including HTML body
    """

    def __init__(self):
        # You can keep these in .env
        self.tenant_id = os.getenv("GRAPH_TENANT_ID")
        self.client_id = os.getenv("GRAPH_CLIENT_ID")
        self.client_secret = os.getenv("GRAPH_CLIENT_SECRET")
        # Sender mailbox (UPN) used in /users/{id|UPN}/sendMail
        self.sender_upn = os.getenv("GRAPH_SENDER_UPN")  # e.g. svc-automation@sandisk.com

        if not self.sender_upn:
            raise ValueError("Missing env var: GRAPH_SENDER_UPN")

    def authenticate(self) -> str:
        """
        Client Credentials token for Microsoft Graph.
        Requires:
          GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET
        """
        if not self.tenant_id:
            raise ValueError("Missing env var: GRAPH_TENANT_ID")
        if not self.client_id:
            raise ValueError("Missing env var: GRAPH_CLIENT_ID")
        if not self.client_secret:
            raise ValueError("Missing env var: GRAPH_CLIENT_SECRET")

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "client_id": os.getenv("GRAPH_CLIENT_ID"),
            "client_secret": os.getenv("GRAPH_CLIENT_SECRET"),
            "grant_type":'password',
            "scope": ' '.join(["https://graph.microsoft.com/.default"]),
            "username":os.getenv('USERNAME'),
            "password":os.getenv('PASSWORD')
        }

        resp = requests.post(token_url, data=data,  headers=headers, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Graph token failure: {resp.status_code} {resp.text}")

        return resp.json()["access_token"]

    def send_html_mail(self, subject: str, html_body: str, recipients: List[str]) -> Dict[str, Any]:
        """
        Sends an HTML email to recipients.
        Returns dict with status info.
        """
        access_token = self.authenticate()
        graph_endpoint = f"https://graph.microsoft.com/v1.0/users/{self.sender_upn}/sendMail"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_body
                },
                "toRecipients": [{"emailAddress": {"address": r}} for r in recipients],
            },
            "saveToSentItems": "true"
        }
        resp = requests.post(graph_endpoint, headers=headers, json=payload,verify=False, timeout=20)

        return {
            "ok": resp.status_code == 202,
            "status_code": resp.status_code,
            "response_text": resp.text[:500]
        }
    
def _health_report_to_html(report_dict: Dict[str, Any]) -> str:
    """
    Build a readable HTML email body from the preflight report dict.
    """
    overall = report_dict.get("overall", "UNKNOWN")
    ts = report_dict.get("timestamp_ms", 0)

    # Convert timestamp_ms to human-readable (optional)
    try:
        ts_readable = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        ts_readable = str(ts)

    rows = []
    for r in report_dict.get("results", []):
        name = r.get("name")
        status = r.get("status")
        mandatory = r.get("mandatory")
        latency = r.get("latency_ms")
        details = json.dumps(r.get("details", {}), indent=2)

        color = "#22c55e" if status == "OK" else ("#f59e0b" if status == "SKIP" else "#ef4444")
        rows.append(f"""
          <tr>
            <td style="padding:8px;border:1px solid #ddd;">{name}</td>
            <td style="padding:8px;border:1px solid #ddd;color:{color};font-weight:600;">{status}</td>
            <td style="padding:8px;border:1px solid #ddd;">{mandatory}</td>
            <td style="padding:8px;border:1px solid #ddd;">{latency}</td>
            <td style="padding:8px;border:1px solid #ddd;"><pre style="margin:0;white-space:pre-wrap;">{details}</pre></td>
          </tr>
        """)

    html = f"""
    <html>
      <body style="font-family:Segoe UI, Arial, sans-serif;">
        <h2 style="margin-bottom:0;">🚨 Preflight Health Check FAILED</h2>
        <p style="margin-top:6px;">
          <b>Overall:</b> <span style="color:#ef4444;font-weight:700;">{overall}</span><br/>
          <b>Timestamp:</b> {ts_readable}
        </p>

        <h3>Check Results</h3>
        <table style="border-collapse:collapse;width:100%;font-size:13px;">
          <thead>
            <tr style="background:#f3f4f6;">
              <th style="padding:8px;border:1px solid #ddd;text-align:left;">Name</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left;">Status</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left;">Mandatory</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left;">Latency (ms)</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:left;">Details</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>

        <p style="margin-top:16px;color:#6b7280;">
          This is an automated notification from Preflight Health Monitoring.
        </p>
      </body>
    </html>
    """
    return html


def notify_developers_on_health_fail(report, *, subject_prefix: str = "[PRECHECK][FAIL]") -> None:
    """
    Sends an email to developers if preflight report is FAIL.
    - report can be PreflightReport (your dataclass) or dict
    """
    try:
        # Convert to dict
        if hasattr(report, "to_json"):
            report_dict = json.loads(report.to_json(indent=2))
        elif isinstance(report, dict):
            report_dict = report
        else:
            report_dict = {"overall": "UNKNOWN", "results": [], "raw": str(report)}

        if report_dict.get("overall") == "OK":
            return  # nothing to send
        subject_prefix =os.getenv("SERVICENAME","")
        recipients_env = os.getenv("HEALTH_FAIL_RECIPIENTS")
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]
        if not recipients:
            logging.warning("HEALTH_FAIL_RECIPIENTS not set; skipping email notification.")
            return
        
        subject = f"{subject_prefix} Preflight health check failed"
        html_body = _health_report_to_html(report_dict)
        mailer = GraphMailer()
        print(f"recipients{recipients}")
        result = mailer.send_html_mail(subject, html_body, recipients)

        if result.get("ok"):
            logging.info("Health fail email sent successfully.")
        else:
            logging.error(f"Failed to send health fail email: {result}")

    except Exception as e:
        # Never crash your main flow because notification failed
        logging.exception(f"notify_developers_on_health_fail error: {e}")    
