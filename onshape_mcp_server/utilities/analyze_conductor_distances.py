#!/usr/bin/env python3
"""
Analyze conductor distances (clearances) between parts in an OnShape document.

This script calculates distances between all parts for clearance verification,
useful for electrical safety compliance.

Usage:
    python analyze_conductor_distances.py <document_id> [workspace_id] [--min-distance MM]
    
Example:
    python analyze_conductor_distances.py 394aa47131b35eec8c9ea996 e7c40af452b8e6b2531d26ee --min-distance 10
"""

import asyncio
import sys
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
from onshape_mcp.api.parts import PartsAPI
from onshape_mcp.api.clearance import ClearanceAnalyzer


async def analyze_distances(document_id: str, workspace_id: str = None, min_distance_mm: float = 0.0):
    """
    Analyze distances between all parts for clearance verification.
    
    Args:
        document_id: OnShape document ID
        workspace_id: Optional workspace ID
        min_distance_mm: Minimum required distance in millimeters
    """
    print(f"Analyzing conductor distances in document: {document_id}")
    if workspace_id:
        print(f"Workspace: {workspace_id}")
    if min_distance_mm > 0:
        print(f"Minimum required distance: {min_distance_mm}mm")
    print("-" * 60)
    
    client = OnShapeClient()
    parts_api = PartsAPI(client)
    analyzer = ClearanceAnalyzer(parts_api)
    
    try:
        # Get elements
        if not workspace_id:
            workspaces = await client.get(f"/documents/d/{document_id}/workspaces")
            if workspaces and len(workspaces) > 0:
                workspace_id = workspaces[0].get("id")
        
        if not workspace_id:
            print("Error: Workspace ID required")
            return
        
        elements = await client.get(f"/documents/d/{document_id}/w/{workspace_id}/elements")
        
        all_parts = []
        
        # Collect all parts from all Part Studios
        for element in elements:
            if element.get("elementType") == "PARTSTUDIO":
                elem_id = element.get("id")
                try:
                    parts = await parts_api.get_all_parts(document_id, workspace_id, elem_id)
                    for part in parts:
                        part_id = part.get("partId") or part.get("id")
                        part_name = part.get("name") or part.get("partName") or part_id
                        all_parts.append({
                            "part_id": part_id,
                            "name": part_name,
                            "element_id": elem_id,
                            "element_name": element.get("name", "Unnamed")
                        })
                except Exception as e:
                    print(f"Warning: Could not get parts from {elem_id}: {e}", file=sys.stderr)
        
        if not all_parts:
            print("No parts found in document.")
            return
        
        print(f"\nFound {len(all_parts)} parts")
        print("Calculating accurate distances using OnShape measure API...\n")
        
        if len(all_parts) < 2:
            print("Need at least 2 parts to calculate distances.")
            return
        
        # Calculate distances between all pairs using measure API
        min_distance_m = min_distance_mm / 1000.0  # Convert to meters
        results = []
        total_pairs = len(all_parts) * (len(all_parts) - 1) // 2
        pair_count = 0
        
        for i, part1 in enumerate(all_parts):
            for part2 in all_parts[i+1:]:
                pair_count += 1
                print(f"Measuring {part1['name']} <-> {part2['name']} ({pair_count}/{total_pairs})...", end="\r", file=sys.stderr)
                
                try:
                    # Use measure API for accurate distance calculation
                    distance = await analyzer.get_minimum_distance(
                        document_id, workspace_id, part1["element_id"],
                        part1["part_id"], part2["part_id"]
                    )
                    
                    if distance is not None:
                        meets_requirement = distance >= min_distance_m
                        results.append({
                            "part1": part1["name"],
                            "part1_id": part1["part_id"],
                            "part2": part2["name"],
                            "part2_id": part2["part_id"],
                            "distance_mm": distance * 1000,  # Convert to mm
                            "meets_requirement": meets_requirement,
                            "status": "PASS" if meets_requirement else "FAIL"
                        })
                    else:
                        results.append({
                            "part1": part1["name"],
                            "part1_id": part1["part_id"],
                            "part2": part2["name"],
                            "part2_id": part2["part_id"],
                            "distance_mm": None,
                            "meets_requirement": False,
                            "status": "ERROR",
                            "error": "Could not calculate distance"
                        })
                except Exception as e:
                    results.append({
                        "part1": part1["name"],
                        "part1_id": part1["part_id"],
                        "part2": part2["name"],
                        "part2_id": part2["part_id"],
                        "distance_mm": None,
                        "meets_requirement": False,
                        "status": "ERROR",
                        "error": str(e)
                    })
        
        print("\n" + " " * 60 + "\r", end="", file=sys.stderr)  # Clear progress line
        
        # Sort by distance (closest first), handling None values
        results.sort(key=lambda x: x["distance_mm"] if x["distance_mm"] is not None else float('inf'))
        
        # Print results
        print("=" * 60)
        print("CONDUCTOR DISTANCE ANALYSIS RESULTS")
        print("=" * 60)
        print()
        
        if min_distance_mm > 0:
            fails = [r for r in results if not r["meets_requirement"]]
            passes = [r for r in results if r["meets_requirement"]]
            
            print(f"Summary:")
            print(f"  Total pairs analyzed: {len(results)}")
            print(f"  Pass (≥{min_distance_mm}mm): {len(passes)}")
            print(f"  Fail (<{min_distance_mm}mm): {len(fails)}")
            print()
            
            if fails:
                print("FAILING PAIRS (below minimum distance):")
                print("-" * 60)
                for result in fails[:20]:  # Show first 20 failures
                    print(f"✗ {result['part1']} <-> {result['part2']}")
                    if result['distance_mm'] is not None:
                        print(f"    Distance: {result['distance_mm']:.2f}mm (required: {min_distance_mm}mm)")
                    else:
                        print(f"    Distance: ERROR - {result.get('error', 'Could not calculate')}")
                    print(f"    Part IDs: {result['part1_id']} <-> {result['part2_id']}")
                    print()
                if len(fails) > 20:
                    print(f"... and {len(fails) - 20} more failures")
                print()
        
        print("CLOSEST PAIRS (top 10):")
        print("-" * 60)
        for result in results[:10]:
            status_icon = "✓" if result.get("meets_requirement", False) else "✗"
            print(f"{status_icon} {result['part1']} <-> {result['part2']}")
            if result['distance_mm'] is not None:
                print(f"    Distance: {result['distance_mm']:.2f}mm")
            else:
                print(f"    Distance: ERROR - {result.get('error', 'Could not calculate')}")
            if min_distance_mm > 0:
                print(f"    Status: {result.get('status', 'UNKNOWN')}")
            print()
        
        # Note about method used
        print("\n✓ Distance calculations use OnShape's evDistance via FeatureScript.")
        print("   Results are accurate surface-to-surface measurements.")
        
        return results
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze conductor distances for clearance verification"
    )
    parser.add_argument("document_id", help="OnShape document ID")
    parser.add_argument("workspace_id", nargs="?", help="OnShape workspace ID")
    parser.add_argument(
        "--min-distance",
        type=float,
        default=0.0,
        help="Minimum required distance in millimeters (default: 0.0)"
    )
    
    args = parser.parse_args()
    
    await analyze_distances(
        args.document_id,
        args.workspace_id,
        args.min_distance
    )


if __name__ == "__main__":
    asyncio.run(main())
