from ..services import TrackingService

tracking_service = TrackingService()

async def fetch_tracking_data(tracking_number: str) -> dict:
    """Fetch tracking information from shipping API."""
    return tracking_service.get_tracking_info(tracking_number)
