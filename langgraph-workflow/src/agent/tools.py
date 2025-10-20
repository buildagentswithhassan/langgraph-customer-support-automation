from langchain_core.tools import tool
import httpx
import logging

logger = logging.getLogger(__name__)


@tool
async def fetch_tracking_data(tracking_number: str) -> dict:
    """Fetch tracking information from shipping API."""
    print("Inside Tool: fetch_tracking_data")
    return {
        "tracking_number": tracking_number,
        "status": "In Transit",
        "last_update": "2025-09-01T15:00:00Z",
        "estimated_delivery": "2025-09-08",
        "days_in_transit": 6,
        "order_id": "6184",
        "carrier": "FedEx",
        "location": "Distribution Center, New York, NY",
    }


@tool
async def search_policy(query: str) -> str:
    """Search company policy and knowledge base for relevant information."""
    print("Inside Tool: search_policy")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/search-kb", params={"query": query}
        )
        response.raise_for_status()
        data = response.json()
        return data["results"]


tools = [fetch_tracking_data, search_policy]
