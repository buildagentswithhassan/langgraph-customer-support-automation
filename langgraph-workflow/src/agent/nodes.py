import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .state import SupportState, EmailParseOutput, DraftResponseOutput, HtmlOutput
from .llm import llm
from .prompts import (
    PARSE_EMAIL_PROMPT,
    ANALYZE_PROBLEM_PROMPT,
    DRAFT_RESPONSE_PROMPT,
    HTML_CONVERTER_PROMPT,
)
from langchain_core.messages import ToolMessage
from pprint import pprint
from datetime import datetime, timezone

# This will be set by the workflow when MCP tools are loaded
llm_with_tools = None
todays_date = datetime.now(timezone.utc).date().isoformat()


def set_llm_with_tools(tools):
    """Set the LLM with tools after MCP tools are loaded."""
    global llm_with_tools
    llm_with_tools = llm.bind_tools(tools)


def parse_email(state: SupportState) -> SupportState:
    """Extract structured information from customer email."""
    try:
        print("Inside Node: parse_email")
        prompt = PARSE_EMAIL_PROMPT.format(
            subject=state["subject"], email_body=state["email_body"]
        )
        response = llm.with_structured_output(EmailParseOutput).invoke(prompt)

        return {
            **state,
            "problem": response.problem,
            "sentiment": response.sentiment,
            "tracking_number": response.tracking_number,
            "order_id": response.order_id,
        }
    except Exception as e:
        print(f"parse_email error: {e}")
        return state


def analyze_problem(state: SupportState):
    """The brain of the operation. Decides the next step based on the parsed email and available data."""
    print("Inside Node: analyze_problem")

    if llm_with_tools is None:
        raise RuntimeError(
            "LLM with tools not initialized. Call set_llm_with_tools() first."
        )

    pprint(
        {
            "problem": state["problem"],
            "sentiment": state["sentiment"],
            "tracking_number": state["tracking_number"],
            "tracking_data": state.get("tracking_data", "None"),
            "order_id": state.get("order_id", "None"),
            "todays_date": todays_date,
        }
    )

    prompt = ANALYZE_PROBLEM_PROMPT.format(
        problem=state["problem"],
        sentiment=state["sentiment"],
        tracking_number=state["tracking_number"],
        tracking_data=state.get("tracking_data", "None"),
        policy_info=state.get("policy_info", "None"),
        order_id=state.get("order_id", "None"),
        todays_date=todays_date,
    )

    response = llm_with_tools.invoke(prompt)

    print("LLM response", response)

    return {**state, "messages": state.get("messages", []) + [response]}


def handle_tool_result(state: SupportState) -> SupportState:
    """Extract tool results and save to appropriate state fields."""
    print("Inside Node: handle_tool_result")

    last_message = state["messages"][-1]

    # print(last_message)

    if isinstance(last_message, ToolMessage):
        tool_name = last_message.name

        if tool_name == "fetch_tracking_data":
            return {**state, "tracking_data": last_message.content}
        elif tool_name == "search_policy":
            return {**state, "policy_info": last_message.content}

    return state


def draft_response(state: SupportState) -> SupportState:
    """Generate professional email response based on problem analysis and available data."""
    print("Inside Node: draft_response")

    messages = state["messages"]
    last_message = messages[-1]

    prompt = DRAFT_RESPONSE_PROMPT.format(
        problem=state["problem"],
        sentiment=state["sentiment"],
        from_email=state["from_email"],
        order_id=state.get("order_id", "None"),
        tracking_data=state.get("shipping_data", "None"),
        policy_info=state.get("policy_info", "None"),
        todays_date=todays_date,
        analysis=last_message.content,
    )
    response = llm.with_structured_output(DraftResponseOutput).invoke(prompt)

    return {
        **state,
        "response_subject": response.subject,
        "response_body": response.body,
    }


def format_to_html_and_send(state: SupportState) -> SupportState:
    """Convert email response to HTML format and prepare for sending."""
    print("Inside Node: format_to_html_and_send")

    prompt = HTML_CONVERTER_PROMPT.format(response_body=state["response_body"])
    response = llm.with_structured_output(HtmlOutput).invoke(prompt)

    subject = state["response_subject"]
    to_email = state["from_email"]
    body = response.html

    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    from_email = os.getenv("GMAIL_USER")

    # Create a multipart message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Attach the body (HTML)
    html_part = MIMEText(body, "html")
    msg.attach(html_part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, gmail_app_password)
            server.send_message(msg)
        return {**state, "response_html_body": body}
    except Exception as e:
        print(str(e))
        return state
