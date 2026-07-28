from tracemalloc import start
from typing import Dict, Any, Callable, Tuple

import requests
import os
from src.services.cyberark.cyberark import cyberark
import json
import time
from dotenv import load_dotenv
from src.config import health_config
import socket
# -----------------------------
# Built-in Checks
# -----------------------------
    



def check_servicenow_api(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    """
    ServiceNow ODBC/SQL-over-HTTP connectivity check.

    Validates that the ServiceNow ODBC endpoint is reachable AND credentials are valid by running a
    minimal SQL query (safe, low-cost):

        POST  {SERVICENOW_ODBC_URL}
        Body: SELECT TOP 1 * FROM task

    Required environment variables:
      - SERVICENOW_ODBC_URL
      - SERVICENOW_ODBC_AUTH_HEADER   (full Authorization header value, e.g. "Bearer xxx" or "Basic yyy")

    Returns:
      ("OK"|"FAIL", latency_ms, {"url":..., "status_code":..., "reason":...})
    """
    # Resolve URL + auth from env (fail fast if missing)
    url = os.getenv("SERVICENOW_ODBC_URL")
    auth_header = os.getenv("SERVICENOW_ODBC_AUTH_HEADER")

    if not url:
        return "FAIL", 0, {"error": "Missing env var: SERVICENOW_ODBC_URL"}
    if not auth_header:
        return "FAIL", 0, {"error": "Missing env var: SERVICENOW_ODBC_AUTH_HEADER"}

    headers = {
        "Authorization": auth_header,
        'Content-Type': 'application/json'
    }
    cb = cyberark(os.getenv("CYBERARK_UID"))
    pwd = cb.get_cyberark_object()['password']
    sql = cfg.get("sql") or " SELECT TOP 1 number FROM task"
    data = json.dumps({
            'sqlstatement': sql,
            "uid": os.getenv("CYBERARK_UID"),
            "pwd": pwd,
            "url": os.getenv("SERVICENOW_INSTANCE")
    })
  
    start = time.perf_counter()
    # Use your retry helper for the actual request (single call)
    
    try:
        resp = requests.post(url=url, headers=headers, data=data)
        latency = (time.perf_counter() - start) * 1000
        resp_json = resp.json()
        return ("OK" if  resp_json["status"]=="success" else "FAIL"), latency, {
            "url": url,
            "status_code":  resp_json["status"],
            "reason":resp_json["result"],
            "query": "SELECT TOP 1 * FROM task"
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return "FAIL", latency_ms, {
            "account_id": os.getenv("SERVICENOW_INSTANCE"),
            "error": str(e),
        }



def check_cyberark_api(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    """
    CyberArk direct API connectivity & authentication check.

    This validates:
      - Network connectivity
      - Auth (AppID / token / cert)
      - Vault access permissions

    It does this by fetching a known safe test secret.

    cfg required keys:
      - test_account_id   (or whatever identifier your wrapper expects)
    """
    test_account_id = cfg.get("test_account_id")
    if not test_account_id:
        return "FAIL", 0, {"error": "Missing cfg.test_account_id for CyberArk check"}

    start = time.perf_counter()
    try:
        cb = cyberark(test_account_id)
        # ✅ REAL CyberArk API call (depends on your wrapper)
        secret = cb.get_cyberark_object()['password']

        latency_ms = (time.perf_counter() - start) * 1000

        if not secret:
            return "FAIL", latency_ms, {
                "reason": "CyberArk returned empty secret",
                "account_id": test_account_id,
            }

        return "OK", latency_ms, {
            "account_id": test_account_id,
            "message": "CyberArk API reachable and authenticated",
        }

    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return "FAIL", latency_ms, {
            "account_id": test_account_id,
            "error": str(e),
        }



def check_powershell_group_api(cfg: Dict[str, Any],common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    """
    PowerShell Get Group / User API connectivity check.

    Equivalent to:
      curl --location 'http://uls-op-itauto02.corp.sandisk.com/powershell/group/<GROUP>'

    Validates:
      - Network connectivity
      - API availability
      - Auth (if headers provided)
      - Measures latency
    """

    url = cfg.get("url") or os.getenv("POWERSHELL_URL")
    if not url:
        return "FAIL", 0, {"error": "Missing PowerShell API URL"}

    headers = cfg.get("headers", {})
    timeout_s = common.get("timeout_s", 8)
    group_id=os.getenv('SAMPLE_GROUP_ID')

    start = time.perf_counter()
    try:
        resp = requests.get(
            url=url+"group/"+ group_id,
            headers=headers,
            timeout=timeout_s,
            verify=False  # internal corp endpoint
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        return (
            "OK" if 200 <= resp.status_code < 300 else "FAIL",
            latency_ms,
            {
                "url": url,
                "status_code": resp.status_code,
            }
        )               
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return "FAIL", latency_ms, {
            "group_id": group_id,
            "error": str(e),
        }



def check_powershell_adduser_api(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    group_name = os.getenv("SAMPLE_GROUP_ID")
    base_url = os.getenv("POWERSHELL_URL")
    upn = os.getenv("SAMPLE_USER")  # or cfg.get("upn")

    if not group_name:
        return "FAIL", 0, {"error": "Missing env var: ADGROUPNAME"}
    if not base_url:
        return "FAIL", 0, {"error": "Missing env var: POWERSHELL_URL"}
    if not upn:
        return "FAIL", 0, {"error": "Missing env var: SAMPLE_USER"}

    base = base_url.rstrip("/")
    url = f"{base}/group/{group_name}/user/{upn}"
    start = time.perf_counter()
    resp = requests.post(url, timeout=common.get("timeout_s", 10), verify=False)
    try:        
        latency_ms = int((time.perf_counter() - start) * 1000)
        payload = resp.json()
        return "OK", latency_ms, {"url": url, "status_code": resp.status_code, "note": "Non-JSON 2xx response"}
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return "FAIL", latency_ms, {
            "group_name": group_name,
            "upn":upn,
            "error": str(e),
        }



def check_env_variables(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:
    """Check environment configuration"""
    
    REQUIRED_ENV_VARS = [
        'SERVICENOW_URL',
        'SERVICENOW_BASE_URL',
        'SMTP_HOSTNAME',
        'SMTP_PORT',
        'SHARED_MAILBOX',
        'ENVIRONMENT'
    ]
    
    load_dotenv()
    start = time.perf_counter()
    print("Handler:",os.getenv('HANDLERS'))
    """Check for required environment variables"""
    missing_vars = []
    empty_vars = []
        
    for var in REQUIRED_ENV_VARS:
        if var not in os.environ:
                missing_vars.append(var)
        elif not os.environ[var].strip():
                empty_vars.append(var)
    latency_ms = int((time.perf_counter() - start) * 1000)    
    if missing_vars or empty_vars:
            issues = []
            if missing_vars:
                issues.append(f"Missing: {', '.join(missing_vars)}")
            if empty_vars:
                issues.append(f"Empty: {', '.join(empty_vars)}")
            return "FAIL", latency_ms, {
                 "service":"CONFIGURATIONHEALTHCHECK",
                 "status":"FAIL",
                 "message":f"Configuration issues: {'; '.join(issues)}",
                 "details":{
                    'missing_vars': missing_vars,
                    'empty_vars': empty_vars
                }}    
    else:    
            latency_ms = int((time.perf_counter() - start) * 1000)
            return "OK", latency_ms, {
                 "service":"CONFIGURATIONHEALTHCHECK",
                 "status":"OK",
                "message":"All required environment variables are configured"}

        
def SmtpHealthCheck(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]:    

        """Check SMTP connectivity"""
        hostname = os.getenv('SMTP_HOSTNAME')
        port = int(os.getenv('SMTP_PORT', 587))

        """Check SMTP server connectivity"""
        if not hostname:
            return "FAIL", 0, {"error": "SMTP hostname not configured"}          
        
        try:
            import time
            import smtplib
            
            start_time = time.time()
            
            # Test SMTP connectivity
            server = smtplib.SMTP(hostname, port)
            server.starttls()
            latency_ms = time.time() - start_time
            server.quit()
            
            return "OK", latency_ms, {
                 "service":"SMTP",
                 "status":"OK",
                "message":f"SMTP server is accessible ({hostname}:{port})",
                 "details":{
                    'hostname': hostname,
                    'port': port
                }
            }            
        
        except socket.timeout:
            return "FAIL", 0, {"error": f"SMTP connection timeout (>{timeout}s)"}          

        except socket.gaierror as e:
            return "FAIL", 0, {"error": f"Cannot resolve SMTP hostname '{hostname}': {str(e)}"} 
            
        except Exception as e:
            return "FAIL", 0, {"error": f"SMTP connection failed: {str(e)}"}

        		



def DnsHealthCheck(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]: 
        """Check DNS resolution"""   

        test_hosts = [('github.com', 'GitHub'),('google.com', 'Google'),('sandisk.com', 'SanDisk Corp')]

        """Check DNS resolution"""
        failed_hosts = []
        
        for hostname, label in test_hosts:
            try:
                socket.gethostbyname(hostname)
            except socket.gaierror:
                failed_hosts.append(f"{label} ({hostname})")
        
        if failed_hosts:
            return "FAIL", 0, {
                 "service":"DnsHealthCheck",
                 "status":"OK",
                 "message":f"Cannot resolve: {', '.join(failed_hosts)}",
                 "details":{'failed_hosts': failed_hosts}
            }            
        
        else:
            return "OK", 0, {
                 "service":"DnsHealthCheck",
                 "status":"OK",
                "message":f"Cannot resolve: {', '.join(failed_hosts)}",
                "details":"DNS resolution is working"
            }


def PythonDependenciesHealthCheck(cfg: Dict[str, Any], common: Dict[str, Any]) -> Tuple[str, int, Dict[str, Any]]: 
    """Check Python dependencies"""    
    REQUIRED_PACKAGES = ['requests','dotenv','selenium']
    
    """Check if required Python packages are installed"""
    missing_packages = []
        
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
        
        if missing_packages:
            return "FAIL", 0, {
                "service":"PythonDependenciesHealthCheck",
                "status":"OK",
                "message":f"Missing Python packages: {', '.join(missing_packages)}",
                "details":{'missing_packages': missing_packages}
            }

        return "OK", 0, {
                "service":"PythonDependenciesHealthCheck",
                "status":"OK",
                "message":"All required Python packages are installed"

            }
        



CHECK_REGISTRY: Dict[
    str,
    Callable[[Dict[str, Any], Dict[str, Any]], Tuple[str, int, Dict[str, Any]]]
] = {
        "cyberark_API": check_cyberark_api,
        "servicenow_API":check_servicenow_api,
        "powershell_API1":check_powershell_group_api,
        "powershell_API2":check_powershell_adduser_api,
        "ConfigurationHealthCheck":check_env_variables,
        "SmtpHealthCheck":SmtpHealthCheck,
        "DnsHealthCheck":DnsHealthCheck,
        "PythonDependenciesHealthCheck":PythonDependenciesHealthCheck
     }
