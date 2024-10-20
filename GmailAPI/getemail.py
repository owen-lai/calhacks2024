from email import message
from GmailAPI.util import authenticate, get_service
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
    labelIds = message['labelIds']

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
    
    service.users().messages().modify(userId=user_id, id=message_id, body={'removeLabelIds': ["UNREAD"]}).execute()

    return thread_id, message_id, subject, sender, body, labelIds

def get_email_attachments(service, user_id, message_id):
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
    email_data = message['payload']
    if 'parts' in email_data:
        for part in email_data['parts']:
            if part['filename']:
                attachment_id = part['body']['attachmentId']
                attachment = service.users().messages().attachments().get(userId=user_id, messageId=message_id, id=attachment_id).execute()
                file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                path = os.path.join("test_sig/", part['filename'])
                print(path)

                # Save the attachment to the specified directory
                with open(path, 'wb') as f:
                    f.write(file_data)
                
                print(f"Attachment {part['filename']} saved to {path}")
                return part['filename']


def get_latest_email():

    try:
        # Call the Gmail API to fetch a list of emails
        service = get_service()
        results = service.users().messages().list(userId='me', maxResults=10, q="label:inbox").execute()
        messages = results.get('messages', [])

        # print(results)
        if not messages:
            print("No messages found.")
            return
        else:
            message_id = messages[0]['id']
            thread_id, message_id, subject, sender, body, labelIds = get_email_message(service, "me", message_id)
            if "UNREAD" in labelIds:
                pdfPath = get_email_attachments(service, "me", message_id)
            else:
                pdfPath = ""
            return thread_id, message_id, subject, sender, body, labelIds, pdfPath
            # print(message)

    except HttpError as error:
        print(f"An error occurred: {error}")

# Add this line in your main function after creating the service object
if __name__ == "__main__":
  list_emails()
