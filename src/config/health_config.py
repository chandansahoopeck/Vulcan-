HEALTH_CHECKS = {
    "CYBERARK": {
        "type": "cyberark_API",
        "mandatory": True,
        "enabled": True,
        "test_account_id": "RPA_TOOL",
    },
    "SERVICENOW": {
        "type": "servicenow_API",
        "mandatory": True,
        "enabled": True,
    },
    "POWERSHELL_GROUP": {
        "type": "powershell_API1",
        "mandatory": True,
        "enabled": False,
    },
    "POWERSHELL_ADDUSER": {
        "type": "powershell_API2",
        "mandatory": True,
        "enabled": False,
    },
    "CONFIGURATION_HEALTHCHECK": {
        "type": "ConfigurationHealthCheck",
        "mandatory": True,
        "enabled": True,
    },

    "SmtpHealthCheck": {
        "type": "SmtpHealthCheck",
        "mandatory": True,
        "enabled": True,
    },
   "DnsHealthCheck":{
        "type":"DnsHealthCheck",
        "mandatory": True,
        "enabled": False,
    },
     "PythonDependenciesHealthCheck":{
        "type":"PythonDependenciesHealthCheck",
        "mandatory": True,
        "enabled": True,
    }

    
}
