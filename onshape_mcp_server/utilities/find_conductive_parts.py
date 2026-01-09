#!/usr/bin/env python3
"""
Script to search for parts with conductive material parameters in an OnShape document.

Usage:
    python find_conductive_parts.py <document_id> [workspace_id]
    
Example:
    python find_conductive_parts.py abc123def456
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from parent directory
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / ".env"
load_dotenv(env_path)

# Add parent directory to path to import onshape_mcp
sys.path.insert(0, str(parent_dir))

from onshape_mcp.api.client import OnShapeClient
from onshape_mcp.api.parts import PartsAPI


# Common conductive materials (case-insensitive)
CONDUCTIVE_MATERIALS = [
    'copper', 'cu', 'brass', 'bronze', 'aluminum', 'al', 'steel', 'stainless steel',
    'silver', 'ag', 'gold', 'au', 'tin', 'lead', 'zinc', 'nickel', 'iron',
    'conductive', 'metal', 'metallic', 'alloy'
]


async def get_all_parts_in_document(client: OnShapeClient, document_id: str, workspace_id: str = None):
    """
    Get all parts from all Part Studios in a document.
    
    Args:
        client: OnShapeClient instance
        document_id: OnShape document ID
        workspace_id: Optional workspace ID (uses default if not provided)
        
    Returns:
        List of dicts with part information including element_id
    """
    parts_api = PartsAPI(client)
    
    # Get all elements (Part Studios and Assemblies) - works even for STEP imports
    try:
        if not workspace_id:
            # Try to get workspaces first
            try:
                workspaces = await client.get(f"/documents/d/{document_id}/workspaces")
                if workspaces and len(workspaces) > 0:
                    workspace_id = workspaces[0].get("id")
            except:
                pass
        
        if not workspace_id:
            print("Error: Workspace ID required for STEP imports")
            return []
        
        # Get all elements (Part Studios and Assemblies)
        elements = await client.get(f"/documents/d/{document_id}/w/{workspace_id}/elements")
        
        all_parts = []
        
        for element in elements:
            element_id = element.get("id")
            element_type = element.get("elementType")
            
            # Only process Part Studios
            if element_type == "PARTSTUDIO":
                try:
                    parts = await parts_api.get_all_parts(document_id, workspace_id, element_id)
                    if isinstance(parts, list):
                        for part in parts:
                            if isinstance(part, dict):
                                part["element_id"] = element_id
                                part["element_name"] = element.get("name", "Unnamed")
                                all_parts.append(part)
                            else:
                                # Handle case where part is just an ID string
                                all_parts.append({
                                    "partId": part,
                                    "id": part,
                                    "element_id": element_id,
                                    "element_name": element.get("name", "Unnamed")
                                })
                except Exception as e:
                    print(f"Warning: Could not get parts from element {element_id}: {e}", file=sys.stderr)
        
        return all_parts
        
    except Exception as e:
        print(f"Error getting document info: {e}", file=sys.stderr)
        return []


async def get_part_material(client: OnShapeClient, document_id: str, workspace_id: str, 
                           element_id: str, part_id: str):
    """
    Get material information for a part.
    
    Args:
        client: OnShapeClient instance
        document_id: OnShape document ID
        workspace_id: Workspace ID
        element_id: Element (Part Studio) ID
        part_id: Part ID
        
    Returns:
        Material name/ID or None
    """
    try:
        # Try to get part metadata which may include material
        part_info = await client.get(
            f"/parts/d/{document_id}/w/{workspace_id}/e/{element_id}/partid/{part_id}"
        )
        
        # Material might be in different places depending on OnShape API version
        material = (
            part_info.get("material") or
            part_info.get("materialId") or
            part_info.get("appearance") or
            part_info.get("properties", {}).get("material")
        )
        
        return material
        
    except Exception as e:
        # Try alternative endpoint for material properties
        try:
            metadata = await client.get(
                f"/metadata/d/{document_id}/w/{workspace_id}/e/{element_id}/p/{part_id}"
            )
            return metadata.get("material") or metadata.get("materialId")
        except:
            return None


def is_conductive(material: str) -> bool:
    """
    Check if a material is conductive.
    
    Args:
        material: Material name or identifier
        
    Returns:
        True if material appears to be conductive
    """
    if not material:
        return False
    
    material_lower = str(material).lower()
    
    # Check against known conductive materials
    for conductive in CONDUCTIVE_MATERIALS:
        if conductive in material_lower:
            return True
    
    return False


async def find_conductive_parts(document_id: str, workspace_id: str = None):
    """
    Find all parts with conductive materials in a document.
    
    Args:
        document_id: OnShape document ID
        workspace_id: Optional workspace ID
    """
    print(f"Searching for conductive parts in document: {document_id}")
    if workspace_id:
        print(f"Workspace: {workspace_id}")
    print("-" * 60)
    
    client = OnShapeClient()
    parts_api = PartsAPI(client)
    
    try:
        # Test authentication first (skip document info check for STEP imports)
        print("Testing authentication...")
        try:
            # Try to get elements instead of document info (works for STEP imports)
            elements = await client.get(f"/documents/d/{document_id}/w/{workspace_id}/elements")
            print("✓ Authentication successful")
        except Exception as auth_error:
            if "401" in str(auth_error) or "Unauthorized" in str(auth_error):
                print("✗ Authentication failed: 401 Unauthorized")
                print("\nPossible causes:")
                print("  1. API key doesn't have access to this document")
                print("  2. Document is private and API key lacks permissions")
                print("  3. API key credentials are incorrect")
                print(f"\nError details: {auth_error}")
                return
            else:
                raise
        
        # Get all parts in the document
        print("Fetching all parts from document...")
        all_parts = await get_all_parts_in_document(client, document_id, workspace_id)
        
        if not all_parts:
            print("No parts found in document.")
            return
        
        print(f"Found {len(all_parts)} parts. Checking materials...\n")
        
        conductive_parts = []
        
        for part in all_parts:
            part_id = part.get("partId") or part.get("id")
            element_id = part.get("element_id")
            element_name = part.get("element_name", "Unknown")
            part_name = part.get("name") or part.get("partName") or part_id
            
            # Get material
            material = await get_part_material(
                client, document_id, workspace_id or "default", element_id, part_id
            )
            
            if is_conductive(material):
                conductive_parts.append({
                    "part_id": part_id,
                    "part_name": part_name,
                    "element_id": element_id,
                    "element_name": element_name,
                    "material": material
                })
                print(f"✓ {part_name} (Material: {material})")
                print(f"  Part ID: {part_id}")
                print(f"  Element: {element_name} ({element_id})")
                print()
        
        print("-" * 60)
        print(f"\nFound {len(conductive_parts)} conductive parts out of {len(all_parts)} total parts.")
        
        if conductive_parts:
            print("\nSummary:")
            for part in conductive_parts:
                print(f"  - {part['part_name']}: {part['material']}")
        
        return conductive_parts
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    document_id = sys.argv[1]
    workspace_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    await find_conductive_parts(document_id, workspace_id)


if __name__ == "__main__":
    asyncio.run(main())
