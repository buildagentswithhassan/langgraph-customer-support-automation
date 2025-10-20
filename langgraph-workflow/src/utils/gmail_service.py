import pickle
import os
from google.auth.transport import requests as google_requests
from googleapiclient.discovery import build


def get_gmail_service():
    """Build an authenticated Gmail API client using saved credentials."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google_requests.Request())
        else:
            raise Exception("No valid credentials available. Run the watch script first.")

    return build("gmail", "v1", credentials=creds)
