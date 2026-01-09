#!/usr/bin/env python3
"""
Script to list all documents accessible via the OnShape API.

Usage:
    python list_documents.py [--limit N] [--query "search term"]
    
Options:
    --limit N       Limit results to N documents (default: 50)
    --query "term"  Search for documents matching term
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from parent directory
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / ".env"
load_dotenv(env_path)

# Add parent directory to path to import onshape_mcp
sys.path.insert(0, str(parent_dir))

from onshape_mcp.api.client import OnShapeClient


async def list_documents(limit: int = 50, query: str = None):
    """
    List all documents accessible via the API.
    
    Args:
        limit: Maximum number of documents to return
        query: Optional search query
    """
    print("Fetching accessible documents from OnShape API...")
    print("-" * 60)
    
    client = OnShapeClient()
    
    try:
        # Try different endpoints to list documents
        endpoints_to_try = [
            ("/documents", {"limit": limit, "offset": 0}),
            ("/documents/search", {"limit": limit}),
        ]
        
        if query:
            endpoints_to_try[0][1]["q"] = query
            endpoints_to_try[1][1]["q"] = query
            print(f"Searching for documents matching: '{query}'")
        
        response = None
        used_endpoint = None
        
        for endpoint, params in endpoints_to_try:
            try:
                print(f"Trying endpoint: {endpoint}...")
                response = await client.get(endpoint, params=params)
                used_endpoint = endpoint
                break
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    print(f"  ✗ Access denied to {endpoint}")
                    continue
                else:
                    raise
        
        if not response:
            print("\n✗ Could not access documents endpoint.")
            print("\nPossible causes:")
            print("  1. API key may not have permission to list documents")
            print("  2. API key may need to be associated with a user account")
            print("  3. Try accessing specific documents by ID instead")
            print("\nHow to get document IDs:")
            print("  - From OnShape URL: https://cad.onshape.com/documents/{DOCUMENT_ID}/...")
            print("  - Share documents with the API key user to grant access")
            print("\nYou can test access to a specific document with:")
            print("  python test_document_access.py <document_id>")
            return
        
        print(f"✓ Successfully accessed {used_endpoint}\n")
        
        documents = response.get("items", [])
        
        if not documents:
            print("No documents found.")
            if query:
                print(f"Try a different search term or check if you have access to any documents.")
            return
        
        print(f"Found {len(documents)} document(s):\n")
        
        for i, doc in enumerate(documents, 1):
            doc_id = doc.get("id", "Unknown")
            name = doc.get("name", "Unnamed")
            owner = doc.get("owner", {})
            owner_name = owner.get("name", "Unknown") if owner else "Unknown"
            created_at = doc.get("createdAt", "Unknown")
            modified_at = doc.get("modifiedAt", "Unknown")
            
            # Get default workspace
            default_workspace = doc.get("defaultWorkspace", {})
            workspace_id = default_workspace.get("id", "Unknown")
            
            print(f"{i}. {name}")
            print(f"   Document ID: {doc_id}")
            print(f"   Workspace ID: {workspace_id}")
            print(f"   Owner: {owner_name}")
            print(f"   Created: {created_at}")
            print(f"   Modified: {modified_at}")
            print(f"   URL: https://cad.onshape.com/documents/{doc_id}/w/{workspace_id}")
            print()
        
        print("-" * 60)
        print(f"\nTotal: {len(documents)} document(s)")
        
        if len(documents) == limit:
            print(f"\nNote: Limited to {limit} results. Use --limit to get more.")
        
        return documents
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="List all documents accessible via OnShape API"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of documents to return (default: 50)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Search query to filter documents"
    )
    
    args = parser.parse_args()
    
    await list_documents(limit=args.limit, query=args.query)


if __name__ == "__main__":
    asyncio.run(main())
