"""MCP tools for OnShape terminal allocation and clearance analysis."""

from mcp.types import Tool
from typing import List

# Import tool definitions and initialization
from .terminal_tools import (
    get_terminal_info,
    verify_terminal_exists,
    analyze_terminal_clearances,
    get_terminal_bounding_box,
    initialize_tools
)
from .clearance_verification import (
    verify_clearance_requirements,
    initialize_verification_tools
)

# Export all tools
__all__ = [
    "get_terminal_info",
    "verify_terminal_exists",
    "analyze_terminal_clearances",
    "get_terminal_bounding_box",
    "verify_clearance_requirements",
    "initialize_tools",
    "get_all_tools"
]


def get_all_tools() -> List[Tool]:
    """Get all available MCP tools."""
    return [
        get_terminal_info,
        verify_terminal_exists,
        analyze_terminal_clearances,
        get_terminal_bounding_box,
        verify_clearance_requirements
    ]
