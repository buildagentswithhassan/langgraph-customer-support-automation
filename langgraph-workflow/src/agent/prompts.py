from langchain.prompts import PromptTemplate

PARSE_EMAIL_PROMPT = PromptTemplate(
    input_variables=["subject", "email_body"],
    template="""
You are a customer support AI. Extract the following information from the customer's email:
- The core problem: one sentence summary.
- The customer's sentiment: angry, frustrated, calm, etc.
- Any order ID or tracking number present in the email.

Subject: {subject}
Email: {email_body}
""",
)

ANALYZE_PROBLEM_PROMPT = PromptTemplate(
    input_variables=[
        "problem",
        "sentiment",
        "tracking_number",
        "tracking_data",
        "policy_info",
        "order_id",
        "todays_date",
    ],
    template="""Analyze the customer's problem and decide the next action.

PROBLEM: {problem}
SENTIMENT: {sentiment}
TRACKING NUMBER: {tracking_number}
ORDER ID: {order_id}
Current Date: {todays_date}

CURRENT DATA:
Tracking Data: {tracking_data}
Policy Data: {policy_info}

DECISION RULES:
1. For delivery/tracking issues: You need BOTH tracking data AND policy data to provide proper resolution
2. For other issues: Determine if you need tracking data, policy data, or both
3. Only proceed without tools if you have ALL necessary information to resolve the issue
4. Carefully review the tracking data if available, before calling 'fetch_tracking_data' tool

Available tools:
- 'fetch_tracking_data': Get tracking status and delivery info, Tracking number is required
- 'search_policy': Get company policies for refunds, returns, etc.

Make your decision based on whether you can resolve the customer's issue with current data.
""",
)

DRAFT_RESPONSE_PROMPT = PromptTemplate(
    input_variables=[
        "problem",
        "sentiment",
        "from_email",
        "tracking_data",
        "policy_info",
        "order_id",
        "analysis",
        "todays_date",
    ],
    template="""You are a customer support agent. Draft a professional, empathetic email response.

Today's Date: {todays_date}

CUSTOMER DETAILS:
Email: {from_email}
Problem: {problem}
Sentiment: {sentiment}
ORDER ID: {order_id}

AVAILABLE DATA:
Tracking Data: {tracking_data}
Policy Information: {policy_info}

LLM Analysis:  {analysis}

INSTRUCTIONS:
1. Address the customer by name if possible, and understand the problem
2. Acknowledge their {sentiment} tone appropriately
3. Analyze the tracking data and policy info to determine the resolution
4. Provide clear next steps or compensation based on company policy
5. Be professional and empathetic

Write a complete email response:""",
)


HTML_CONVERTER_PROMPT = PromptTemplate(
    input_variables=["response_body"],
    template="""Convert the following email response to clean, professional HTML format.

EMAIL CONTENT:
{response_body}

REQUIREMENTS:
- Use proper HTML structure with clean formatting
- Make it professional and easy to read
- Preserve all content and meaning
- Use appropriate HTML tags for structure

Return only the HTML content:""",
)
