#!/usr/bin/env python3
"""
Test access to a specific OnShape document.

Usage:
    python test_document_access.py <document_id>
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from parent directory
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(parent_dir))

from onshape_mcp.api.client import OnShapeClient


async def test_document_access(document_id: str):
    """Test if we can access a specific document."""
    print(f"Testing access to document: {document_id}")
    print("-" * 60)
    
    client = OnShapeClient()
    
    try:
        # Try to get document info
        # OnShape API format: /documents/{did} (not /documents/d/{did})
        # The /d/ prefix is only for workspace-specific operations
        print("Attempting to access document...")
        doc_info = await client.get(f"/documents/{document_id}")
        
        print("✓ Document access successful!\n")
        
        name = doc_info.get("name", "Unknown")
        owner = doc_info.get("owner", {})
        owner_name = owner.get("name", "Unknown") if owner else "Unknown"
        
        # Get workspaces
        workspaces = await client.get(f"/documents/d/{document_id}/workspaces")
        default_workspace = doc_info.get("defaultWorkspace", {})
        workspace_id = default_workspace.get("id", "Unknown")
        
        print(f"Document Name: {name}")
        print(f"Document ID: {document_id}")
        print(f"Owner: {owner_name}")
        print(f"Default Workspace ID: {workspace_id}")
        print(f"Total Workspaces: {len(workspaces) if workspaces else 0}")
        print(f"\nURL: https://cad.onshape.com/documents/{document_id}/w/{workspace_id}")
        
        # Try to get elements (Part Studios)
        try:
            elements = await client.get(f"/documents/d/{document_id}/w/{workspace_id}/elements")
            if elements:
                print(f"\nElements (Part Studios/Assemblies): {len(elements)}")
                for elem in elements[:5]:  # Show first 5
                    print(f"  - {elem.get('name', 'Unnamed')} ({elem.get('elementType', 'Unknown')})")
                if len(elements) > 5:
                    print(f"  ... and {len(elements) - 5} more")
        except Exception as e:
            print(f"\nCould not list elements: {e}")
        
        return True
        
    except Exception as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            print("✗ Access denied to this document")
            print("\nTo grant access:")
            print("  1. Open the document in OnShape")
            print("  2. Click 'Share' button")
            print("  3. Add the API key user or grant permissions")
        else:
            print(f"✗ Error: {e}")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    document_id = sys.argv[1]
    success = asyncio.run(test_document_access(document_id))
    sys.exit(0 if success else 1)
