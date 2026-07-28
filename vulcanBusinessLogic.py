

# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 14:26:48 2023

@author: 7347743
"""

import os
import zipfile
import py7zr
import shutil
# from distutils.dir_util import copy_tree
import shutil
from os.path import join

import requests
import time
from datetime import datetime
import pytz
from src.services.constants.constants import *
from src.services.cyberark.cyberark import cyberark
from dotenv import load_dotenv
from xyops_metrics import XYOpsMetrics
from SuccessEmailLogs import *

load_dotenv(override=True)
print("envloaded successfully")

metrics = XYOpsMetrics()
start = time.time()

metrics.total_mail_processed_run.labels(job="xyops_job",workflow="xyops").set(0)
metrics.mail_processed_run.labels(job="xyops_job", workflow="xyops").set(0)
metrics.mail_processed_failed_run.labels(job="xyops_job",workflow="xyops").set(0)

metrics.job_status.labels("xyops_job", "xyops").set(1)

cb = cyberark("graph_api_mailbox")
auth = cb.get_cyberark_object()


'''def pushmetrics(id):
    if(id == 1 ):
        print("Entered in to Success Metric Path")
        #metrics.job_status.labels("xyops_job", "xyops").set(1)                                
        # ✅ per‑run
        metrics.mail_processed_run.labels("xyops_job", "xyops").inc()
        # ✅ lifetime
        metrics.total_mail_processed_run.labels("xyops_job", "xyops").inc()
    elif (id == 0):
        print("Entered in to Failed Metric Path")
        #metrics.job_status.labels("xyops_job", "xyops").set(0)
        # ✅ per‑run
        metrics.mail_processed_failed_run.labels("xyops_job", "xyops").inc()
        # ✅ lifetime
        metrics.mail_ignored_total.labels("xyops_job", "xyops").inc()'''


def extract_variables_from_name(name):
    name_vars = str(name).split('_')
    file_ext = name_vars[len(name_vars) - 1]
    file_ext_vars = str(file_ext).split(".")
    log_type = file_ext_vars[0]
    return {
        'user': name_vars[0],
        'type': log_type,
        'date': name_vars[3] if len(name_vars) > 4 else ''
    }

def file_new_name_without_user(name):
    name_vars = str(name).split('_')
    name_vars.pop(0)
    new_name = '_'.join(name_vars)
    return new_name

#process mails
def process_mails(attachments, dest_folder,message_id):
    for attach_file in attachments:
        attachment_id = attach_file.get('id')
        attachment_name = attach_file.get('name')
        attachment_download_url = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/attachments/{attachment_id}/$value"
        headers = _get_access_token()
        attachment_response = requests.get(attachment_download_url, headers=headers, stream=True, verify= False)
        if attachment_response.status_code == 200:
            # for attachment in attachments:
            # Save the attachment to a file
            attachment_path = os.path.join(download_folder, attachment_name)
            with open(attachment_path, 'wb') as f:
                for chunk in attachment_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the attachment contents - support both .zip and .7z files
            try:
                # Check file extension to determine extraction method
                if attachment_name.lower().endswith('.7z'):
                    # Extract .7z file
                    print(f"Extracting .7z file: {attachment_name}")
                    with py7zr.SevenZipFile(attachment_path, mode='r') as z:
                        z.extractall(path=unzip_folder)
                elif attachment_name.lower().endswith('.zip'):
                    # Extract .zip file
                    print(f"Extracting .zip file: {attachment_name}")
                    with zipfile.ZipFile(attachment_path, 'r') as zip_ref:
                        zip_ref.extractall(unzip_folder)
                else:
                    print(f"Unsupported file format: {attachment_name}")
                    # Remove the downloaded file and skip processing
                    os.remove(attachment_path)
                    continue
            except Exception as e:
                print(f"Error extracting file {attachment_name}: {e}")
                # Remove the problematic file and continue with next attachment
                if os.path.exists(attachment_path):
                    os.remove(attachment_path)
                continue
            
            # Remove the downloaded compressed file
            os.remove(attachment_path)
            
            # Process the extracted files
            for f in os.listdir(unzip_folder):
                current_file = os.path.join(unzip_folder, f)
                # Check if the current item exists before processing
                if not os.path.exists(current_file):
                    print(f"Skipping {f} - file not found at {current_file}")
                    continue
                    
                vars = extract_variables_from_name(f)
                dest_date_folder = os.path.join(dest_folder, vars['date'])
                dest_date_user_folder = os.path.join(dest_date_folder, vars['user'] + '_' + vars['type'])
                
                # Create destination folders if they don't exist
                if not os.path.exists(dest_date_folder):
                    os.makedirs(dest_date_folder, exist_ok=True)
                if not os.path.exists(dest_date_user_folder):
                    os.makedirs(dest_date_user_folder, exist_ok=True)
                
                new_name = file_new_name_without_user(f)
                dest_file_path = os.path.join(dest_date_user_folder, new_name)
                
                # Handle files and directories separately
                if os.path.isfile(current_file):
                    # Copy file
                    shutil.copyfile(current_file, dest_file_path)
                    os.remove(current_file)
                    print(f"Processed file: {f} -> {dest_file_path}")
                elif os.path.isdir(current_file):
                    # Copy directory
                    if os.path.exists(dest_file_path):
                        shutil.rmtree(dest_file_path)
                    shutil.copytree(current_file, dest_file_path)
                    shutil.rmtree(current_file)
                    print(f"Processed folder: {f} -> {dest_file_path}")

# function to move mails to folder
def move(name):
    headers = _get_access_token()
    response = requests.get(f'{graph_endpoint_folder}/mailFolders?$top=100', headers=headers, verify= False)
    #print(f"response_move: {response}")
    # Check the response status code
    if response.status_code == 200:
        folders = response.json().get('value', [])
        for folder in folders:
            folder_name = folder.get('displayName', '')
            folder_id = folder.get('id', '')
            if str(name) == str(folder_name):
                return folder_id
            else:
                continue

def process_mails_new(attachments, dest,message_id):
    for attach_file in attachments:
        attachment_id = attach_file.get('id')
        attachment_name = attach_file.get('name')
        attachment_download_url = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/attachments/{attachment_id}/$value"
        headers = _get_access_token()
        attachment_response = requests.get(attachment_download_url, headers=headers, stream=True)
        if attachment_response.status_code == 200:
            # for attachment in attachments:
            # Save the attachment to a file
            attachment_path = os.path.join(download_folder, attachment_name)
            with open(attachment_path, 'wb') as f:
                for chunk in attachment_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the attachment contents - support both .zip and .7z files
            try:
                # Check file extension to determine extraction method
                if attachment_name.lower().endswith('.7z'):
                    # Extract .7z file
                    print(f"Extracting .7z file: {attachment_name}")
                    with py7zr.SevenZipFile(attachment_path, mode='r') as z:
                        z.extractall(path=unzip_folder)
                elif attachment_name.lower().endswith('.zip'):
                    # Extract .zip file
                    print(f"Extracting .zip file: {attachment_name}")
                    with zipfile.ZipFile(attachment_path, 'r') as zip_ref:
                        zip_ref.extractall(unzip_folder)
                else:
                    print(f"Unsupported file format: {attachment_name}")
                    # Remove the downloaded file and skip processing
                    os.remove(attachment_path)
                    continue
            except Exception as e:
                print(f"Error extracting file {attachment_name}: {e}")
                # Remove the problematic file and continue with next attachment
                if os.path.exists(attachment_path):
                    os.remove(attachment_path)
                continue
            
            # Remove the downloaded compressed file
            os.remove(attachment_path)
            
            # Create destination folder if it doesn't exist
            if not os.path.exists(dest):
                os.makedirs(dest, exist_ok=True)
            
            # Process the extracted files
            for f in os.listdir(unzip_folder):
                current_file = os.path.join(unzip_folder, f)
                dest_file_path = os.path.join(dest, f)
                
                # Check if the current item exists before processing
                if not os.path.exists(current_file):
                    print(f"Skipping {f} - file not found at {current_file}")
                    continue
                
                # Handle files and directories separately
                if os.path.isfile(current_file):
                    # Copy file
                    shutil.copyfile(current_file, dest_file_path)
                    os.remove(current_file)
                    print(f"Processed file: {f} -> {dest_file_path}")
                elif os.path.isdir(current_file):
                    # Copy directory
                    if os.path.exists(dest_file_path):
                        shutil.rmtree(dest_file_path)
                    shutil.copytree(current_file, dest_file_path)
                    shutil.rmtree(current_file)
                    print(f"Processed folder: {f} -> {dest_file_path}")

def update_serviceTimeStamp(serviceName, mailCounts):

    import requests


    try:

        url = f"http://uls-op-itexau01.ad.shared/service?servicename={serviceName}&mailCounts={mailCounts}"

        payload = {}

        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload, verify= False)

        print(response.text)

    except Exception as err:

        print(f"{err}")   
        
def _get_access_token():
    mailCounts = 0
    token_response = requests.post(token_url, data=token_data, verify= False)
    access_token = token_response.json().get('access_token')
    # Get the messages from the shared mailbox
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
        }   
    return headers              

def vulcanBusinessLogic():
        
    # smtp config fields
    smtp_username = os.getenv('smtp_username')
    tenant_id = os.getenv('tenant_id')
    client_id = os.getenv('client_id')
    client_name = os.getenv('client_name')
    smtp_scope = os.getenv('smtp_scope')
    smtp_token_url = os.getenv('smtp_token_url')
    smtp_graph_url = os.getenv('smtp_graph_url')
    smtp_hostname = os.getenv('smtp_hostname')
    smtp_port = os.getenv('smtp_port')


    cb = cyberark(client_name)
    auth = cb.get_cyberark_object()
    client_secret = auth['password']
    while True:
        try:
            mailCounts = 0
            token_response = requests.post(token_url, data=token_data, verify= False)
            #print(token_response.json())
            # print(token_response.json())
            access_token = token_response.json().get('access_token')
            # print(access_token)
            # Get the messages from the shared mailbox
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            messages_url = f"{graph_endpoint}/messages"
            messages_response = requests.get(messages_url, headers=headers, verify= False)
            if messages_response.status_code == 200:
                messages = messages_response.json().get('value')
                if len(messages) > 0:
                    mailCounts  = len(messages)
                    #add metrics
                    for message in messages:
                        try:
                            message_id = message['id']
                            message_subject = message['subject']
                            print(f'subject: {message_subject}')
                            attachments_url = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/attachments"
                            attachments_response = requests.get(attachments_url, headers=headers, verify= False)
                            if attachments_response.status_code == 200:
                                attachments = attachments_response.json().get('value')
                                #pushmetrics(1)
                                if len(attachments) > 0:
                                    if 'vulcan pilot' in message_subject.lower():
                                        process_mails(attachments, dest_folder,message_id)
                                        vulcan_folder = move("vulcan")
                                        move_payload = {'destinationId': vulcan_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    elif 'shuri pilot' in message_subject.lower():
                                        print(Shuri_Pilot_folder)
                                        process_mails(attachments, Shuri_Pilot_folder,message_id)
                                        vulcan_folder = move("Shuri Pilot")
                                        move_payload = {'destinationId': vulcan_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    elif 'clover pilot' in message_subject.lower():
                                        process_mails(attachments, clover_dest_folder,message_id)
                                        clover_folder = move("clover")
                                        move_payload = {'destinationId': clover_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    elif 'hIOmon' in message_subject:
                                        tz = pytz.timezone('Asia/Jerusalem')
                                        now = datetime.now(tz).strftime("%m-%d-%Y")
                                        dest_with_date = join(script_dest, str(now))
                                        process_mails_new(attachments, dest_with_date, message_id)
                                        hIOmon_folder = move("hIOmon")
                                        move_payload = {'destinationId': hIOmon_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    elif 'vivaldi pilot' in message_subject.lower():
                                        process_mails(attachments, vivaldi_dest_folder,message_id)
                                        vivaldi_folder = move("Vivaldi Pilot")
                                        move_payload = {'destinationId': vivaldi_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    
                                    elif 'atlas3' in message_subject.lower():
                                        print("Atlas")
                                        process_mails(attachments, Atlas_dest_folder,message_id)
                                        atlas_folder = move("Atlas3")
                                        move_payload = {'destinationId': atlas_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    
                                    elif 'maia2 pilot' in message_subject.lower():
                                        print("MAIA2 Pilot")
                                        process_mails(attachments, MAIA2Pilot_dest_folder,message_id)
                                        MAIA2_Pilot_folder = move("MAIA2 Pilot")
                                        move_payload = {'destinationId': MAIA2_Pilot_folder}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    else:
                                        unrecognized = move("unrecognized")
                                        move_payload = {'destinationId': unrecognized}
                                        move_response = requests.post(f"https://graph.microsoft.com/v1.0/users/{shared_mailbox}/messages/{message_id}/move", headers=headers, json=move_payload, verify= False)
                                    if move_response.status_code == 201:
                                        print("Email moved successfully.")
                                        log_email_success(message_subject)
                                    #pushmetrics(1)
                                    else:
                                        print(f"Failed to move email: {move_response.text}")
                                    #pushmetrics(0)
                        except Exception as err:
                            #pushmetrics(0)
                            raise Exception(str(err))
                else:
                    print(f"No mail in shared mailbox:{datetime.now()}")
                    #pushmetrics(0)
            time.sleep(3)
            # update_serviceTimeStamp("Vulcan", mailCounts)
        except Exception as e:
            #pushmetrics(0)
            raise Exception(str(e))
