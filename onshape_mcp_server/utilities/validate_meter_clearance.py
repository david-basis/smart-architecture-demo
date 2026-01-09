#!/usr/bin/env python3
"""
Clearance Validation Exercise: Requirements -> Parts -> OnShape

This script demonstrates the complete validation flow from SysML requirements
through part definitions to OnShape physical verification.

VALIDATION FLOW:
================

1. REQUIREMENTS (SysML):
   - ElectricalClearanceReq (REQ-ELECTRICAL-CLEARANCE-001)
   - States: "Electrical parts shall meet minimum clearance requirements 
     based on voltage and current ratings per IEC 61010-1 and IEC 61439-1 
     standards. Worst case (maximum) clearance is selected from both standards."

2. PARTS (SysML):
   - MeterTerminal part definition satisfies ElectricalClearanceReq
   - IntegratedMeter contains 4 MeterTerminal instances:
     * phaseInTerminal
     * phaseOutTerminal  
     * neutralInTerminal
     * neutralOutTerminal

3. MAPPING (onshape_part_mapping.json):
   - Links SysML part names to OnShape part IDs
   - Defines voltage (230V) and current (80A) for each terminal
   - Specifies clearance pairs to verify:
     * Phase in <-> Phase out
     * Phase in <-> Neutral in
     * Phase out <-> Neutral out

4. ONSHAPE (3D CAD Model):
   - Document: 394aa47131b35eec8c9ea996
   - Physical parts with actual geometry
   - Material properties (synced dynamically)

5. VERIFICATION (MCP Tool):
   - Calculate required clearance from voltage/current (IEC standards)
   - Query OnShape for actual surface-to-surface distances (FeatureScript)
   - Compare actual vs required
   - Report compliance status

Usage:
    python validate_meter_clearance.py
"""

import asyncio
import sys
import json
from pathlib import Path
import os

# Try to load .env, but don't fail if it doesn't work
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except:
    pass

# Add parent directory to path to import onshape_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from onshape_mcp.api.client import OnShapeClient
from onshape_mcp.tools.clearance_verification import (
    initialize_verification_tools,
    handle_verify_clearance_requirements
)


async def validate_meter_clearance():
    """Execute clearance validation for meter terminals."""
    print("=" * 70)
    print("CLEARANCE VALIDATION EXERCISE")
    print("Requirements -> Parts -> OnShape")
    print("=" * 70)
    print()
    
    print("VALIDATION FLOW:")
    print("-" * 70)
    print("1. REQUIREMENTS (SysML):")
    print("   - ElectricalClearanceReq (REQ-ELECTRICAL-CLEARANCE-001)")
    print("   - IEC 61010-1 and IEC 61439-1 standards")
    print()
    print("2. PARTS (SysML):")
    print("   - MeterTerminal parts in IntegratedMeter")
    print("   - Satisfies ElectricalClearanceReq")
    print()
    print("3. MAPPING:")
    print("   - onshape_part_mapping.json links SysML to OnShape")
    print("   - Defines voltage (230V), current (80A) per terminal")
    print()
    print("4. ONSHAPE:")
    print("   - Document: 394aa47131b35eec8c9ea996")
    print("   - Physical 3D geometry")
    print()
    print("5. VERIFICATION:")
    print("   - Calculate required clearance (IEC standards)")
    print("   - Query actual distances (FeatureScript)")
    print("   - Compare and report compliance")
    print()
    print("=" * 70)
    print()
    
    client = None
    try:
        # Initialize client
        print("Initializing OnShape client...")
        client = OnShapeClient()
        initialize_verification_tools(client)
        print("✓ Client initialized")
        print()
        
        # Load mapping and verify
        print("Loading part mapping...")
        mapping_file = Path(__file__).parent.parent / "onshape_part_mapping.json"
        if not mapping_file.exists():
            print(f"✗ Mapping file not found: {mapping_file}")
            return
        
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        print(f"✓ Loaded mapping for {len(mapping.get('part_mappings', {}))} terminals")
        print(f"✓ {len(mapping.get('clearance_pairs', []))} clearance pairs to verify")
        print()
        
        # Execute verification
        print("Executing clearance verification...")
        print("-" * 70)
        arguments = {
            "mapping_file": "onshape_part_mapping.json"
        }
        
        results = await handle_verify_clearance_requirements(arguments)
        
        # Parse and display results
        print()
        print("=" * 70)
        print("VERIFICATION RESULTS")
        print("=" * 70)
        print()
        
        for result in results:
            if result.type == "text":
                try:
                    data = json.loads(result.text)
                    
                    # Display summary
                    if "total_pairs" in data:
                        print(f"Total pairs analyzed: {data['total_pairs']}")
                        print()
                    
                    # Display each result
                    if "results" in data:
                        passes = [r for r in data["results"] if r.get("status") == "pass"]
                        fails = [r for r in data["results"] if r.get("status") == "fail"]
                        errors = [r for r in data["results"] if r.get("status") == "error"]
                        
                        print(f"Summary: {len(passes)} pass, {len(fails)} fail, {len(errors)} errors")
                        print()
                        
                        for r in data["results"]:
                            status_icon = "✓" if r.get("status") == "pass" else "✗" if r.get("status") == "fail" else "⚠"
                            print(f"{status_icon} {r.get('pair', 'Unknown pair')}")
                            
                            if r.get("status") != "error":
                                print(f"   Terminal 1: {r.get('terminal1')} (Material: {r.get('material1', 'N/A')})")
                                print(f"   Terminal 2: {r.get('terminal2')} (Material: {r.get('material2', 'N/A')})")
                                print(f"   Voltage: {r.get('voltage', 0):.1f}V, Current: {r.get('current', 0):.1f}A")
                                
                                required = r.get("required_clearance_mm")
                                actual = r.get("actual_distance_mm")
                                margin = r.get("margin_mm")
                                
                                if required is not None and actual is not None:
                                    print(f"   Required: {required:.2f}mm")
                                    print(f"   Actual:   {actual:.2f}mm")
                                    if margin is not None:
                                        print(f"   Margin:   {margin:+.2f}mm")
                                
                                # Show clearance by standard
                                clearances = r.get("clearance_description", "")
                                if clearances:
                                    print(f"   {clearances}")
                                
                                print()
                            else:
                                print(f"   Error: {r.get('error', 'Unknown error')}")
                                print()
                except json.JSONDecodeError:
                    print(result.text)
                except Exception as e:
                    print(f"Error parsing results: {e}")
                    print(result.text)
            else:
                print(result)
        
        print("=" * 70)
        print("Validation complete!")
        
    except ValueError as e:
        print(f"✗ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease ensure ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY are set.")
    except Exception as e:
        print(f"✗ Error during validation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        if client:
            await client.close()


if __name__ == "__main__":
    asyncio.run(validate_meter_clearance())
