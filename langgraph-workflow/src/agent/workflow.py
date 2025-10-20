import asyncio
from dotenv import load_dotenv
import json
from functools import partial
from mcp import types
import os

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, ToolMessage
from .state import SupportState
from .nodes import (
    parse_email,
    analyze_problem,
    handle_tool_result,
    draft_response,
    format_to_html_and_send,
    set_llm_with_tools,
)
from .client import MCPClient


load_dotenv(override=True)

server_url = f"{os.getenv("MCP_SERVER_BASE_URL")}/mcp"


# Define router function to handle tool calls
def router(state):
    messages = state["messages"]
    last_message = messages[-1]

    has_tool_calls = False
    if isinstance(last_message, AIMessage):
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            has_tool_calls = True
        elif hasattr(
            last_message, "additional_kwargs"
        ) and last_message.additional_kwargs.get("tool_calls"):
            has_tool_calls = True

    return "tools" if has_tool_calls else "end"


def extract_tool_result(result: types.CallToolResult):
    if result.isError:
        raise RuntimeError(f"Tool returned error: {result}")
    if not result.content:
        return None

    first = result.content[0]
    if hasattr(first, "text"):
        try:
            return json.loads(first.text)
        except json.JSONDecodeError:
            return first.text  # fallback: plain string
    return first


async def async_tool_executor(state, client: MCPClient, tools):
    messages = state["messages"]
    last_message = messages[-1]

    # Check if there are tool calls
    tool_calls = None
    if hasattr(last_message, "tool_calls"):
        tool_calls = last_message.tool_calls
    elif (
        hasattr(last_message, "additional_kwargs")
        and "tool_calls" in last_message.additional_kwargs
    ):
        tool_calls = last_message.additional_kwargs["tool_calls"]

    if not tool_calls:
        return {"messages": messages}

    # Process each tool call
    new_messages = messages.copy()

    for tool_call in tool_calls:
        # Handle different formats of tool_call
        if isinstance(tool_call, dict):
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id", "tool-call-id")
        else:
            tool_name = tool_call.name
            tool_args = tool_call.args if hasattr(tool_call, "args") else {}
            tool_id = getattr(tool_call, "id", "tool-call-id")

        # Print debug info
        print(f"Executing tool: {tool_name}")
        print(f"Tool args: {tool_args}")

        # Find the matching tool
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            # Tool not found
            tool_error = f"Error: {tool_name} is not a valid tool, try one of {[t.name for t in tools]}."
            new_messages.append(AIMessage(content=tool_error))
        else:
            try:
                result = await client.call_tool(tool_name, tool_args)
                extracted_result = extract_tool_result(result)

                # Add tool result
                new_messages.append(
                    ToolMessage(
                        content=str(extracted_result),
                        tool_call_id=tool_id,
                        name=tool_name,
                    )
                )
            except Exception as e:
                # Handle errors
                error_msg = f"Error: {str(e)}\n Please fix your mistakes."
                print(f"Tool error: {error_msg}")
                new_messages.append(AIMessage(content=error_msg))

    return {"messages": new_messages}


async def create_workflow(client: MCPClient):
    """Create LangGraph workflow with MCP tools loaded."""
    try:
        mcp_tools = await client.list_tools()

        # Initialize LLM with MCP tools
        set_llm_with_tools(mcp_tools)

        print(f"Loaded {len(mcp_tools)} MCP tools: {[tool.name for tool in mcp_tools]}")

        # Build the StateGraph
        workflow = StateGraph(SupportState)

        # Add nodes
        workflow.add_node("parse_email", parse_email)
        workflow.add_node("analyze_problem", analyze_problem)
        workflow.add_node(
            "tools", partial(async_tool_executor, client=client, tools=mcp_tools)
        )
        workflow.add_node("handle_tool_result", handle_tool_result)
        workflow.add_node("draft_response", draft_response)
        workflow.add_node("format_to_html_and_send", format_to_html_and_send)

        # Add edges
        workflow.set_entry_point("parse_email")
        workflow.add_edge("parse_email", "analyze_problem")

        # Conditional: analyze_problem > tools OR draft_response
        workflow.add_conditional_edges(
            "analyze_problem",
            router,
            {
                "tools": "tools",
                "end": "draft_response",
            },
        )

        # After tools run, extract results and go back to analyze_problem
        workflow.add_edge("tools", "handle_tool_result")
        workflow.add_edge("handle_tool_result", "analyze_problem")
        workflow.add_edge("draft_response", "format_to_html_and_send")
        workflow.add_edge("format_to_html_and_send", END)

        return workflow.compile()

    except Exception as e:
        print(f"Failed to create workflow: {e}")
        raise


async def save_workflow_graph(app, filename):
    try:
        graph_bytes = app.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(graph_bytes)
    except Exception as e:
        print(f"Failed to save workflow graph: {e}")


async def start_agent_workflow(subject: str, body: str, from_email: str):
    """Main workflow entry point."""
    try:
        async with MCPClient(server_url=server_url) as _client:
            app = await create_workflow(_client)
            await save_workflow_graph(app, "workflow.png")

            initial_state = SupportState(
                email_body=body, subject=subject, from_email=from_email
            )

            result = await app.ainvoke(initial_state)
            print(f"Workflow completed for {from_email}")
            return result
    except Exception as e:
        print(f"Workflow failed for {from_email}: {e}")
        raise
