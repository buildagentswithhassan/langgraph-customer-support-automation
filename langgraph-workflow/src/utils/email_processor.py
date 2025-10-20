import base64
import asyncio
from email import message_from_bytes
from .gmail_service import get_gmail_service
from .history_tracker import get_last_history_id, save_last_history_id


def process_email_notification(email_address, history_id):
    """Background task to process ONLY the new email that triggered the webhook."""
    try:
        print(f"New email notification for: {email_address}, historyId: {history_id}")

        last_processed_id = get_last_history_id()
        service = get_gmail_service()

        if last_processed_id:
            try:
                history_response = (
                    service.users()
                    .history()
                    .list(
                        userId="me",
                        startHistoryId=last_processed_id,
                        historyTypes="messageAdded",
                    )
                    .execute()
                )

                history_items = history_response.get("history", [])
                print(
                    f"Found {len(history_items)} history items since {last_processed_id}"
                )

                new_message_ids = []
                for history_item in history_items:
                    messages_added = history_item.get("messagesAdded", [])
                    for message_added in messages_added:
                        message_id = message_added["message"]["id"]
                        new_message_ids.append(message_id)
                        print(f"New message detected: {message_id}")

                for message_id in new_message_ids:
                    process_single_message(service, message_id)

            except Exception as history_error:
                print(
                    f"History API error, falling back to unread method: {history_error}"
                )
                process_all_unread_messages(service)
        else:
            print("First run: processing all current unread messages")
            process_all_unread_messages(service)

        save_last_history_id(history_id)
        print("Finished processing new emails")

    except Exception as e:
        print(f"Error processing email: {e}")


def process_all_unread_messages(service):
    """Fallback method: process all unread messages (less precise)."""
    messages_response = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=10)
        .execute()
    )

    messages = messages_response.get("messages", [])
    print(f"Found {len(messages)} unread messages in fallback mode")

    for msg in messages:
        message_id = msg["id"]
        process_single_message(service, message_id)


def process_single_message(service, message_id):
    """Process a single message by ID and mark it as read."""
    try:
        print(f"Processing message ID: {message_id}")

        message_response = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="raw")
            .execute()
        )

        msg_str = base64.urlsafe_b64decode(message_response["raw"].encode("ASCII"))
        mime_msg = message_from_bytes(msg_str)

        subject = mime_msg["subject"]
        from_ = mime_msg["from"]
        body = ""

        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = mime_msg.get_payload(decode=True).decode()

        print("Processing Email:")
        print(f"From: {from_}")
        print(f"Subject: {subject}")
        print(f"Body preview: {body[:200]}...")

        # Import here to avoid circular imports
        from ..agent.workflow import start_agent_workflow

        # Start the LangGraph workflow
        asyncio.create_task(start_agent_workflow(subject, body, from_))

        service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        print(f"Marked message {message_id} as read")

    except Exception as e:
        print(f"Error processing single message {message_id}: {e}")
