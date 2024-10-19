from GmailAPI.util import authenticate
import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]

def get_email_message(service, user_id, message_id):
    # Retrieve the email message with the specified message_id
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
    email_data = message['payload']
    headers = email_data['headers']
    thread_id = message['threadId']
    message_id = message['id']

    # Extract the subject, sender, etc.
    subject = None
    sender = None

    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
        if header['name'] == 'From':
            sender = header['value']

    body = ''
    if 'parts' in email_data:
        for part in email_data['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

    return thread_id, message_id, subject, sender, body

def get_latest_email():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("../GmailAPI/token.json"):
        creds = Credentials.from_authorized_user_file("../GmailAPI/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    else:
        creds = authenticate()

    try:
        # Call the Gmail API to fetch a list of emails
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10, q="label:inbox").execute()
        messages = results.get('messages', [])

        # print(results)
        if not messages:
            print("No messages found.")
            return
        else:
            message_id = messages[1]['id']
            thread_id, message_id, subject, sender, body = get_email_message(service, "me", message_id)
            return thread_id, message_id, subject, sender, body
            # print(message)

    except HttpError as error:
        print(f"An error occurred: {error}")

# Add this line in your main function after creating the service object
if __name__ == "__main__":
  list_emails()
