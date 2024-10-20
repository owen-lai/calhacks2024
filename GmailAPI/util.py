import os.path
import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://mail.google.com/"]

def get_service():
    creds = Credentials.from_authorized_user_file("../GmailAPI/token.json", SCOPES)

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
        
    return service

def authenticate():
    creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../GmailAPI/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)
            # Save the credentials for the next run
        with open("../GmailAPI/token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds