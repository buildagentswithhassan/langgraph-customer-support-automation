import base64
import json
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from src.utils import process_email_notification
from src.agent.knowledge_base import kb

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.post("/gmail-webhook")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """Gmail webhook endpoint to receive Pub/Sub notifications."""
    try:
        body = await request.body()
        body_str = body.decode()
        print(f"Raw webhook received: {body_str}")

        request_data = json.loads(body_str)

        # Verify the request (commented out for development, but ESSENTIAL for production)
        # auth_header = request.headers.get('Authorization')
        # verify_pubsub_message(request_data, auth_header)

        message_data = request_data["message"]["data"]
        decoded_data = base64.b64decode(message_data).decode("utf-8")
        pubsub_data = json.loads(decoded_data)

        email_address = pubsub_data["emailAddress"]
        history_id = pubsub_data["historyId"]

        background_tasks.add_task(process_email_notification, email_address, history_id)

        return {"status": "success", "message": "Processing email"}

    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-kb")
async def initialize_knowledge_base():
    """Initialize the knowledge base by loading and indexing the PDF."""
    try:
        kb.load_and_index()
        return {"status": "success", "message": "Knowledge base initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
