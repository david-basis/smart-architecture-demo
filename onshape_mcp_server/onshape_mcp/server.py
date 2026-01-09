"""MCP server for OnShape API terminal allocation and clearance analysis."""

import asyncio
import os
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api.client import OnShapeClient
from .tools import get_all_tools, initialize_tools
from .tools.terminal_tools import (
    handle_get_terminal_info,
    handle_verify_terminal_exists,
    handle_get_terminal_bounding_box,
    handle_analyze_terminal_clearances
)
from .tools.clearance_verification import (
    initialize_verification_tools,
    handle_verify_clearance_requirements
)


# Initialize OnShape client
client: OnShapeClient = None

# Initialize client on module load
try:
    client = OnShapeClient()
    initialize_tools(client)
    initialize_verification_tools(client)
    print("OnShape MCP server initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"Warning: Failed to initialize OnShape client: {e}", file=sys.stderr)
    print("Set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY environment variables", file=sys.stderr)


# Create MCP server
app = Server("onshape-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return get_all_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if not client:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized. Check credentials."
        )]
    
    # Route to appropriate handler
    if name == "get_terminal_info":
        return await handle_get_terminal_info(arguments)
    elif name == "verify_terminal_exists":
        return await handle_verify_terminal_exists(arguments)
    elif name == "get_terminal_bounding_box":
        return await handle_get_terminal_bounding_box(arguments)
    elif name == "analyze_terminal_clearances":
        return await handle_analyze_terminal_clearances(arguments)
    elif name == "verify_clearance_requirements":
        return await handle_verify_clearance_requirements(arguments)
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
