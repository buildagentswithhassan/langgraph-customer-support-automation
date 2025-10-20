from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

PROJECT_ID = "agentic-support-assistant"


def verify_pubsub_message(request_data, auth_header):
    """Verify the Pub/Sub message is from Google."""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    id_info = id_token.verify_oauth2_token(
        token, google_requests.Request(), audience=PROJECT_ID
    )

    if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise ValueError("Invalid issuer.")

    return True
