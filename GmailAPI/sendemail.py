import os.path
import base64
from email.message import EmailMessage
from GmailAPI.util import get_service

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


def gmail_create_draft(subject, body, recipient, messageID, threadID, in_reply_to, references, filepath=None):
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  try:
    # create gmail api client
    service = get_service()

    message = MIMEMultipart()

    message["To"] = recipient
    message["From"] = "ayangsea@gmail.com"
    message["Subject"] = subject
    message['In-Reply-To'] = in_reply_to
    message['References'] = references

    msg = MIMEText(body)
    message.attach(msg)

    filepath = "../fetch/test_sig/scanned_for_signature.pdf"

    if filepath:
      content_type, encoding = "application/octet-stream", None
      main_type, sub_type = content_type.split('/', 1)
      with open(filepath, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(filepath)

      # Create MIMEBase object for the attachment
      attachment = MIMEBase(main_type, sub_type)
      attachment.set_payload(file_data)
      
      # Encode the attachment in base64
      encoders.encode_base64(attachment)

      # Add header to attachment
      attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')

      # Attach the file to the message
      message.attach(attachment)

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message, "threadId": threadID}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    # sent_message = (
    #     service.users()
    #     .drafts()
    #     .send(userId="me", body={"id": draft["id"]})
    #     .execute()
    # )

    # print(f'Message sent! Message Id: {sent_message["id"]}')


  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  return draft


if __name__ == "__main__":
  gmail_create_draft()