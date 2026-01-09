"""MCP tools for clearance requirement verification."""

from mcp.types import Tool, TextContent
from typing import Any, Dict, List, Optional
import json
from pathlib import Path

from ..api.client import OnShapeClient
from ..api.parts import PartsAPI
from ..api.clearance import ClearanceAnalyzer
from ..api.iec_clearance import calculate_clearance, get_clearance_description


# Initialize API clients (will be set by server)
_client: OnShapeClient = None
_parts_api: PartsAPI = None
_clearance_analyzer: ClearanceAnalyzer = None


def initialize_verification_tools(client: OnShapeClient):
    """Initialize verification tools with OnShape client."""
    global _client, _parts_api, _clearance_analyzer
    _client = client
    _parts_api = PartsAPI(client)
    _clearance_analyzer = ClearanceAnalyzer(_parts_api)


def load_part_mapping(mapping_file: str = "onshape_part_mapping.json") -> Dict[str, Any]:
    """
    Load OnShape part mapping from JSON file.
    
    Args:
        mapping_file: Path to mapping file (relative to onshape_mcp_server directory)
        
    Returns:
        Mapping dictionary
    """
    mapping_path = Path(__file__).parent.parent.parent / mapping_file
    if not mapping_path.exists():
        return {}
    
    with open(mapping_path, 'r') as f:
        return json.load(f)


async def get_part_material_from_api(
    document_id: str,
    workspace_id: str,
    element_id: str,
    part_id: str
) -> str:
    """
    Get material for a part from OnShape (sync dynamically).
    
    Args:
        document_id: OnShape document ID
        workspace_id: Workspace ID
        element_id: Element ID
        part_id: Part ID
        
    Returns:
        Material name or "Unknown"
    """
    try:
        # Try to get part metadata which may include material
        part_info = await _parts_api.get_part(document_id, workspace_id, element_id, part_id)
        
        # Material might be in different places depending on OnShape API version
        material = (
            part_info.get("material") or
            part_info.get("materialId") or
            part_info.get("appearance") or
            part_info.get("properties", {}).get("material")
        )
        
        if isinstance(material, dict):
            return material.get("displayName") or material.get("name") or "Unknown"
        return str(material) if material else "Unknown"
    except:
        # Try alternative endpoint for material properties
        try:
            metadata = await _client.get(
                f"/metadata/d/{document_id}/w/{workspace_id}/e/{element_id}/p/{part_id}"
            )
            material = metadata.get("material") or metadata.get("materialId")
            if isinstance(material, dict):
                return material.get("displayName") or material.get("name") or "Unknown"
            return str(material) if material else "Unknown"
        except:
            return "Unknown"


verify_clearance_requirements = Tool(
    name="verify_clearance_requirements",
    description="Verify clearance requirements for terminal pairs using IEC standards. Uses a predefined JSON mapping file.",
    inputSchema={
        "type": "object",
        "properties": {
            "mapping_file": {
                "type": "string",
                "description": "Path to part mapping JSON file",
                "default": "onshape_part_mapping.json"
            }
        },
        "required": []
    }
)


async def handle_verify_clearance_requirements(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle verify_clearance_requirements tool call."""
    if not _parts_api:
        return [TextContent(
            type="text",
            text="Error: OnShape client not initialized"
        )]
    
    try:
        mapping_file = arguments.get("mapping_file", "onshape_part_mapping.json")
        mapping = load_part_mapping(mapping_file)
        
        if not mapping:
            return [TextContent(
                type="text",
                text=f"Error: Could not load mapping file: {mapping_file}"
            )]
        
        document_id = mapping.get("document_id")
        workspace_id = mapping.get("workspace_id")
        element_id = mapping.get("element_id")
        part_mappings = mapping.get("part_mappings", {})
        clearance_pairs = mapping.get("clearance_pairs", [])
        
        if not all([document_id, workspace_id, element_id]):
            return [TextContent(
                type="text",
                text="Error: Mapping file missing document_id, workspace_id, or element_id"
            )]
        
        results = []
        
        # Process each clearance pair
        for pair in clearance_pairs:
            terminal1_name = pair.get("terminal1")
            terminal2_name = pair.get("terminal2")
            pair_desc = pair.get("description", f"{terminal1_name} to {terminal2_name}")
            
            # Get part mappings
            term1_mapping = part_mappings.get(terminal1_name, {})
            term2_mapping = part_mappings.get(terminal2_name, {})
            
            if not term1_mapping or not term2_mapping:
                results.append({
                    "pair": pair_desc,
                    "status": "error",
                    "error": f"Missing mapping for {terminal1_name} or {terminal2_name}"
                })
                continue
            
            part_id1 = term1_mapping.get("onshape_part_id")
            part_id2 = term2_mapping.get("onshape_part_id")
            voltage1 = term1_mapping.get("voltage", 0.0)
            voltage2 = term2_mapping.get("voltage", 0.0)
            current1 = term1_mapping.get("current", 0.0)
            current2 = term2_mapping.get("current", 0.0)
            
            # Use maximum voltage and current for clearance calculation
            max_voltage = max(voltage1, voltage2)
            max_current = max(current1, current2)
            
            # Calculate required clearance
            required_clearance_mm, clearances = calculate_clearance(
                max_voltage, max_current, insulation_type="basic"
            )
            clearance_desc = get_clearance_description(
                max_voltage, max_current, required_clearance_mm, clearances
            )
            
            # Get actual distance from OnShape using PartsAPI directly to get error details
            try:
                distance_result = await _parts_api.get_minimum_distance(
                    document_id, workspace_id, element_id, part_id1, part_id2
                )
                
                if distance_result.get("status") == "success":
                    actual_distance_m = distance_result.get("distance")
                    actual_distance_mm = actual_distance_m * 1000.0 if actual_distance_m else 0.0
                    
                    # Get materials (sync from OnShape)
                    material1 = await get_part_material_from_api(document_id, workspace_id, element_id, part_id1)
                    material2 = await get_part_material_from_api(document_id, workspace_id, element_id, part_id2)
                    
                    # Check compliance
                    meets_requirement = actual_distance_mm >= required_clearance_mm
                    
                    results.append({
                        "pair": pair_desc,
                        "terminal1": terminal1_name,
                        "terminal2": terminal2_name,
                        "part_id1": part_id1,
                        "part_id2": part_id2,
                        "material1": material1,
                        "material2": material2,
                        "voltage": max_voltage,
                        "current": max_current,
                        "required_clearance_mm": required_clearance_mm,
                        "actual_distance_mm": actual_distance_mm,
                        "clearances_by_standard": clearances,
                        "clearance_description": clearance_desc,
                        "meets_requirement": meets_requirement,
                        "status": "pass" if meets_requirement else "fail",
                        "margin_mm": actual_distance_mm - required_clearance_mm
                    })
                else:
                    # Get error details from distance result
                    error_msg = distance_result.get("error", "Could not calculate distance")
                    
                    results.append({
                        "pair": pair_desc,
                        "status": "error",
                        "error": error_msg
                    })
            except Exception as e:
                results.append({
                    "pair": pair_desc,
                    "status": "error",
                    "error": str(e)
                })
        
        # Format results
        output = {
            "document_id": document_id,
            "workspace_id": workspace_id,
            "element_id": element_id,
            "total_pairs": len(clearance_pairs),
            "results": results
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(output, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
