import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "OrderTrackingInfo")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "support-kb")
    COHERE_MODEL = os.getenv("COHERE_MODEL", "embed-english-light-v3.0")
