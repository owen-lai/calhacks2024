import os.path
import base64
from email.message import EmailMessage
import util

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def gmail_create_draft():
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  try:
    # create gmail api client
    service = util.get_service()

    message = EmailMessage()

    message.set_content("Hello")

    message["To"] = "lai.owen@berkeley.edu"
    message["From"] = "ayangsea@gmail.com"
    message["Subject"] = "Hello"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    sent_message = (
        service.users()
        .drafts()
        .send(userId="me", body={"id": draft["id"]})
        .execute()
    )

    print(f'Message sent! Message Id: {sent_message["id"]}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  return draft


if __name__ == "__main__":
  gmail_create_draft()