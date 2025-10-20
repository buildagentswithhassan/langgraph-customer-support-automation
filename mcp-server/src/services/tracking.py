import boto3
from botocore.exceptions import ClientError
from ..config import Settings


class TrackingService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=Settings.AWS_REGION)
        self.table = self.dynamodb.Table(Settings.DYNAMODB_TABLE)

    def get_tracking_info(self, tracking_number: str) -> dict:
        try:
            response = self.table.get_item(Key={"tracking_number": tracking_number})
            
            if "Item" not in response:
                return {"error": "Tracking number not found"}
            
            return response["Item"]
        except ClientError as e:
            return {"error": f"Database error: {e.response['Error']['Message']}"}
