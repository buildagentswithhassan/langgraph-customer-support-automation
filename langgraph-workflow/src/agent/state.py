from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from typing import Annotated, List
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.graph import MessagesState
from pydantic import ConfigDict


class SupportState(MessagesState):
    email_body: str = Field(..., description="Raw email body text")
    subject: str = Field(..., description="Email subject line")
    from_email: str = Field(..., description="Sender email address")

    problem: Optional[str] = Field(
        None, description="One-sentence summary of the customer's issue"
    )
    sentiment: Optional[str] = Field(
        None, description="Customer sentiment: angry, frustrated, calm, etc."
    )
    tracking_number: Optional[str] = Field(
        None, description="Package tracking number, if present"
    )
    order_id: Optional[str] = Field(None, description="Order ID, if present")

    tracking_data: Optional[Dict] = Field(
        None, description="Fetched shipping data if available"
    )
    policy_info: Optional[str] = Field(
        None, description="Company policy information from knowledge base"
    )
    resolution: Optional[Dict] = Field(
        None, description="Proposed resolution for the issue"
    )
    response_subject: Optional[str] = Field(
        None, description="Subject line for the email response"
    )
    response_body: Optional[str] = Field(
        None, description="Complete email body content for customer response"
    )
    response_html_body: Optional[str] = Field(
        None, description="Complete email body in html for customer response"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class EmailParseOutput(BaseModel):
    problem: Optional[str] = Field(
        None, description="One-sentence summary of the customer's issue"
    )
    sentiment: Optional[str] = Field(
        None, description="Customer sentiment: angry, frustrated, calm, etc."
    )
    tracking_number: Optional[str] = Field(
        None, description="Package tracking number, if present"
    )
    order_id: Optional[str] = Field(None, description="Order ID, if present")


class DraftResponseOutput(BaseModel):
    subject: Optional[str] = Field(
        None, description="Subject line for the email response"
    )
    body: Optional[str] = Field(
        None, description="Complete email body content for customer response"
    )


class HtmlOutput(BaseModel):
    html: Optional[str] = Field(None, description="Email response content formatted as clean, professional HTML")
