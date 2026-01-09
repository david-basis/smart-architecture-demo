#!/usr/bin/env python3
"""
Test script for clearance requirement verification.

Usage:
    python test_clearance_verification.py
"""

import asyncio
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path to import onshape_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from onshape_mcp.api.client import OnShapeClient
from onshape_mcp.tools.clearance_verification import (
    initialize_verification_tools,
    handle_verify_clearance_requirements
)


async def test_verification():
    """Test clearance requirement verification."""
    print("Testing Clearance Requirement Verification")
    print("=" * 60)
    
    client = None
    try:
        client = OnShapeClient()
        initialize_verification_tools(client)
        
        # Test with default mapping file
        arguments = {
            "mapping_file": "onshape_part_mapping.json"
        }
        
        print("\nCalling verify_clearance_requirements...")
        results = await handle_verify_clearance_requirements(arguments)
        
        print("\nResults:")
        print("-" * 60)
        for result in results:
            if result.type == "text":
                try:
                    data = json.loads(result.text)
                    print(json.dumps(data, indent=2))
                except:
                    print(result.text)
            else:
                print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        if client:
            await client.close()


if __name__ == "__main__":
    asyncio.run(test_verification())
