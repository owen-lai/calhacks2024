import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]

def get_email_message(service, user_id, message_id):
    # Retrieve the email message with the specified message_id
    message = service.users().messages().get(userId=user_id, id=message_id, format='raw').execute()
    return message

def list_emails():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.

    try:
        # Call the Gmail API to fetch a list of emails
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return
        else:
            message_id = messages[4]['id']
            message = get_email_message(service, "me", message_id)
            print(message)

    except HttpError as error:
        print(f"An error occurred: {error}")

# Add this line in your main function after creating the service object
if __name__ == "__main__":
  list_emails()
