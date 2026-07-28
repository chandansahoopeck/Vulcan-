import os

client_id = "993e679e-3ece-4b69-b4fc-2cf6adcb14665656"
# client_secret = "xFv8Q~9vdP94b.rKdtuLYJkDY5NYLcgdvtj~IcC55A"
client_secret = "WfS8Q~x30TZoKcVL7U5Q4OcoXg6wsNjL55nGsw7dB2"
username = "svc-GSS-RPA@sandisk.com"
password = "ZT9q!%Lff555346Z8-Fy'"
# username='RPA-GSS.Service-Account@sandisk.com'
# password='4QC4X6q4ssf5Hbed'
grant_type = 'password'
tenant_id = "7ffe0sdfff2-35d0-407e-a107-79fc32e84ec4"

#client_secret = 'Smx8Q~6sdfFk.5cFA_Qww60VDeqSznQ1prkjF482a3.'

shared_mailbox = 'CSSD.Pilot.Platform.Logs@sandisk.com'
# shared_mailbox = 'IT-Automation-CheckMk@sandisk.com'
#shared_mailbox = 'IT-Automation-HPC@sandisk.com'
# shared_mailbox = 'gcc-alert-bucket@sandisk.com'
# shared_mailbox = 'CMPP.Philippines@sandisk.com'
# shared_mailbox = 'imc@sandisk.com'
# shared_mailbox = 'GSD-NoReply@sandisk.com'

unzip_folder = r'\\uls-op-genus55.corp.sandisk.com\rpa_data\Projects\vulcan\Unzip'
download_folder = r'\\uls-op-genus55.corp.sandisk.com\rpa_data\Projects\vulcan'
dest_folder = r'\\ulssvmgenip02d-498-d01.corp.sandisk.com\vulcan_pilot_data'
clover_dest_folder = r'\\ibh-op-cssin12.corp.sandisk.com\Datastore1\DataLens\Clover_PILOT'

Atlas_unzip_folder = r'\\uls-op-genus55.corp.sandisk.com\rpa_data\Projects\atlas\Unzip'
Atlas_download_folder = r'\\uls-op-genus55.corp.sandisk.com\rpa_data\Projects\atlas'
Atlas_dest_folder = r'\\ibh-op-cssin12.corp.sandisk.com\Datastore1\DataLens\Atlas_Pilot'

script_dest = r'\\ulssvmgenip02d-498-d01.corp.sandisk.com\vulcan_pilot_data\hIOmon_Bug_Script_Data\FILE_FROM_EMAIL'
vivaldi_dest_folder = r'\\ibn-op-cssin12.corp.sandisk.com\Datastore1\DataLens\Vivaldi Pilot'
MAIA2Pilot_dest_folder = r'\\ibn-op-cssin12.corp.sandisk.com\Datastore1\DataLens\MAIA2Pilot'
Shuri_Pilot_folder = r'\\ibn-op-cssin12.corp.sandisk.com\Datastore1\DataLens\Shuri_Pilot'
scope = ["https://graph.microsoft.com/.default"]
token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
graph_endpoint = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/mailFolders/Inbox"
graph_endpoint_folder = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/"
# Get the access token using client credentials flow
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
token_data = {
    'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': password,
    'scope': 'https://graph.microsoft.com/.default'
}
