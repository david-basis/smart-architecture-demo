#!/usr/bin/env python3
"""Test OnShape API authentication."""

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


async def test_auth():
    """Test OnShape API authentication."""
    print("Testing OnShape API authentication...")
    print("-" * 60)
    
    client = OnShapeClient()
    
    print(f"Access Key: {client.access_key[:15]}...")
    print(f"Secret Key: {'*' * len(client.secret_key)}")
    print()
    
    # Test with a simple endpoint that should work if auth is correct
    try:
        print("Testing API access with /api/users/sessioninfo...")
        response = await client.get("/users/sessioninfo")
        print("✓ Authentication successful!")
        print(f"  User: {response.get('name', 'Unknown')}")
        print(f"  Email: {response.get('email', 'Unknown')}")
        return True
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        # Try to get more details
        try:
            import httpx
            async with httpx.AsyncClient() as test_client:
                headers = client._get_auth_headers()
                test_response = await test_client.get(
                    "https://cad.onshape.com/api/users/sessioninfo",
                    headers=headers
                )
                print(f"\nResponse status: {test_response.status_code}")
                print(f"Response text: {test_response.text[:200]}")
        except Exception as e2:
            print(f"Debug error: {e2}")
        
        if "401" in str(e):
            print("\nThe API key credentials appear to be incorrect or invalid.")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    success = asyncio.run(test_auth())
    sys.exit(0 if success else 1)
