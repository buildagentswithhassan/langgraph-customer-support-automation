from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.routing import Route
from .tools.tracking_tools import fetch_tracking_data
from .tools.knowledge_tools import search_policy


def create_server():
    mcp = FastMCP(
        name="support-assistant-server",
        stateless_http=True,
    )

    mcp.tool()(fetch_tracking_data)
    mcp.tool()(search_policy)

    return mcp


async def health_check(request):
    return JSONResponse({"status": "healthy"})


def get_app():
    server = create_server()
    app = server.streamable_http_app()

    # Add health check route
    app.routes.append(Route("/", health_check, methods=["GET"]))
    app.routes.append(Route("/health", health_check, methods=["GET"]))

    return app
