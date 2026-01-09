"""MCP tools for terminal allocation and verification."""

from mcp.types import Tool, TextContent
from typing import Any
import json

from ..api.client import OnShapeClient
from ..api.parts import PartsAPI
from ..api.clearance import ClearanceAnalyzer


# Initialize API clients (will be set by server)
_client: OnShapeClient = None
_parts_api: PartsAPI = None
_clearance_analyzer: ClearanceAnalyzer = None


def initialize_tools(client: OnShapeClient):
    """Initialize tools with OnShape client."""
    global _client, _parts_api, _clearance_analyzer
    _client = client
    _parts_api = PartsAPI(client)
    _clearance_analyzer = ClearanceAnalyzer(_parts_api)


get_terminal_info = Tool(
    name="get_terminal_info",
    description="Get information about an OnShape terminal/part by ID. Returns part details including geometry references.",
    inputSchema={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "OnShape document ID"
            },
            "workspace_id": {
                "type": "string",
                "description": "OnShape workspace ID"
            },
            "element_id": {
                "type": "string",
                "description": "OnShape element (Part Studio) ID"
            },
            "part_id": {
                "type": "string",
                "description": "OnShape part ID for the terminal"
            }
        },
        "required": ["document_id", "workspace_id", "element_id", "part_id"]
    }
)


async def handle_get_terminal_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_terminal_info tool call."""
    if not _parts_api:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized"
        )]
    
    try:
        part_info = await _parts_api.get_part(
            arguments["document_id"],
            arguments["workspace_id"],
            arguments["element_id"],
            arguments["part_id"]
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(part_info, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


verify_terminal_exists = Tool(
    name="verify_terminal_exists",
    description="Verify that a terminal/part exists in OnShape. Returns true if part exists and is accessible.",
    inputSchema={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "OnShape document ID"
            },
            "workspace_id": {
                "type": "string",
                "description": "OnShape workspace ID"
            },
            "element_id": {
                "type": "string",
                "description": "OnShape element (Part Studio) ID"
            },
            "part_id": {
                "type": "string",
                "description": "OnShape part ID for the terminal"
            }
        },
        "required": ["document_id", "workspace_id", "element_id", "part_id"]
    }
)


async def handle_verify_terminal_exists(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle verify_terminal_exists tool call."""
    if not _parts_api:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized"
        )]
    
    try:
        exists = await _parts_api.verify_part_exists(
            arguments["document_id"],
            arguments["workspace_id"],
            arguments["element_id"],
            arguments["part_id"]
        )
        
        return [TextContent(
            type="text",
            text=json.dumps({"exists": exists, "part_id": arguments["part_id"]})
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


get_terminal_bounding_box = Tool(
    name="get_terminal_bounding_box",
    description="Get bounding box of a terminal for clearance analysis. Returns min/max corners in meters.",
    inputSchema={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "OnShape document ID"
            },
            "workspace_id": {
                "type": "string",
                "description": "OnShape workspace ID"
            },
            "element_id": {
                "type": "string",
                "description": "OnShape element (Part Studio) ID"
            },
            "part_id": {
                "type": "string",
                "description": "OnShape part ID for the terminal"
            }
        },
        "required": ["document_id", "workspace_id", "element_id", "part_id"]
    }
)


async def handle_get_terminal_bounding_box(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_terminal_bounding_box tool call."""
    if not _parts_api:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized"
        )]
    
    try:
        bbox = await _parts_api.get_part_bounding_box(
            arguments["document_id"],
            arguments["workspace_id"],
            arguments["element_id"],
            arguments["part_id"]
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(bbox, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


analyze_terminal_clearances = Tool(
    name="analyze_terminal_clearances",
    description="Analyze clearances between multiple terminals. Calculates distances and verifies against requirements.",
    inputSchema={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "OnShape document ID"
            },
            "workspace_id": {
                "type": "string",
                "description": "OnShape workspace ID"
            },
            "element_id": {
                "type": "string",
                "description": "OnShape element (Part Studio) ID"
            },
            "terminals": {
                "type": "array",
                "description": "List of terminal objects with part_id and optional name",
                "items": {
                    "type": "object",
                    "properties": {
                        "part_id": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["part_id"]
                }
            },
            "required_clearance": {
                "type": "number",
                "description": "Required clearance in meters (default: 0.0)",
                "default": 0.0
            }
        },
        "required": ["document_id", "workspace_id", "element_id", "terminals"]
    }
)


async def handle_analyze_terminal_clearances(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle analyze_terminal_clearances tool call."""
    if not _clearance_analyzer:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized"
        )]
    
    try:
        results = await _clearance_analyzer.analyze_terminal_clearances(
            arguments["document_id"],
            arguments["workspace_id"],
            arguments["element_id"],
            arguments["terminals"],
            arguments.get("required_clearance", 0.0)
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
