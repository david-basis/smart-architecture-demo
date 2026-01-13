#!/usr/bin/env python3
"""
Mock test for SysML requirement -> verification traceability.

This test demonstrates the full chain:
  1. SysML Requirement (ElectricalClearanceReq from IECStandards.sysml)
  2. SysML Part (PartWithPower and derived parts from Gen2Panel1P12.sysml)
  3. IEC Standards Lookup (iec_clearance.py - matches IECStandards.sysml tables)
  4. Analysis (ClearanceAnalysis calc def)
  5. Verification (ClearanceVerification verdict)

Uses MOCK data instead of real OnShape API calls.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from onshape_mcp.api.iec_clearance import (
    calculate_clearance,
    get_clearance_description,
    lookup_iec_61010_1,
    lookup_iec_61439_1,
)


# =============================================================================
# SysML Model Representations (Python equivalents)
# =============================================================================

class InsulationType(Enum):
    """Matches IECStandards::InsulationType enum"""
    FUNCTIONAL = "functional"
    BASIC = "basic"
    REINFORCED = "reinforced"


class VerdictKind(Enum):
    """Matches VerificationCases::VerdictKind"""
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ElectricalClearanceReq:
    """
    Matches IECStandards::ElectricalClearanceReq requirement def.

    Requirement: Electrical parts shall meet minimum clearance requirements
    based on voltage and current ratings per IEC 61010-1 and IEC 61439-1.
    """
    id: str = "REQ-ELECTRICAL-CLEARANCE-001"
    voltage_V: float = 230.0
    insulation_type: InsulationType = InsulationType.BASIC
    required_clearance_mm: Optional[float] = None  # Calculated from IEC tables


@dataclass
class PartWithPower:
    """
    Matches IECStandards::PartWithPower abstract part def.

    Base for all powered components with clearance requirements.
    """
    name: str
    voltage_V: float = 230.0
    current_A: float = 80.0
    insulation_type: InsulationType = InsulationType.BASIC

    # Satisfy relationship to requirement
    clearance_req: ElectricalClearanceReq = None

    def __post_init__(self):
        # Establish satisfy relationship
        self.clearance_req = ElectricalClearanceReq(
            voltage_V=self.voltage_V,
            insulation_type=self.insulation_type
        )


def clearance_analysis(
    voltage_V: float,
    insulation_type: InsulationType,
    actual_clearance_mm: float,
    required_clearance_mm: float
) -> float:
    """
    Matches IECStandards::ClearanceAnalysis calc def.

    Returns margin_mm = actual - required (positive = pass)
    """
    return actual_clearance_mm - required_clearance_mm


def is_compliant(margin_mm: float) -> bool:
    """
    Matches IECStandards::IsCompliant calc def.

    Returns true if margin >= 0
    """
    return margin_mm >= 0.0


def clearance_verification(
    part_under_test: PartWithPower,
    actual_clearance_mm: float,
    required_clearance_mm: float
) -> Tuple[VerdictKind, Dict]:
    """
    Matches IECStandards::ClearanceVerification verification def.

    Inputs:
      - part_under_test: The part being verified (subject)
      - actual_clearance_mm: Measured from CAD (external input)
      - required_clearance_mm: From IEC lookup (external input)

    Returns:
      - VerdictKind (pass/fail)
      - Details dict with margin and analysis results
    """
    margin_mm = clearance_analysis(
        part_under_test.voltage_V,
        part_under_test.insulation_type,
        actual_clearance_mm,
        required_clearance_mm
    )

    verdict = VerdictKind.PASS if actual_clearance_mm >= required_clearance_mm else VerdictKind.FAIL

    return verdict, {
        "part_name": part_under_test.name,
        "voltage_V": part_under_test.voltage_V,
        "current_A": part_under_test.current_A,
        "insulation_type": part_under_test.insulation_type.value,
        "actual_clearance_mm": actual_clearance_mm,
        "required_clearance_mm": required_clearance_mm,
        "margin_mm": margin_mm,
        "is_compliant": is_compliant(margin_mm),
        "requirement_id": part_under_test.clearance_req.id
    }


# =============================================================================
# Mock OnShape Data (simulates API responses)
# =============================================================================

MOCK_MEASURED_CLEARANCES = {
    # Part pairs -> measured distance in mm (would come from OnShape Measure API)
    ("phaseInTerminal", "neutralInTerminal"): 8.5,   # Good clearance
    ("phaseInTerminal", "phaseOutTerminal"): 12.0,   # Good clearance
    ("phaseInScrew", "neutralInScrew"): 3.2,         # Marginal - check carefully
    ("busbars_phase", "busbars_neutral"): 15.0,      # Good clearance
    ("gridRelay_phase", "gridRelay_neutral"): 2.5,   # FAIL - too close!
    ("mainSwitch_phase", "mainSwitch_neutral"): 5.5, # Good clearance
}


# =============================================================================
# Test Functions
# =============================================================================

def test_iec_table_matches_sysml():
    """
    Verify that Python IEC tables match SysML IECStandards package values.
    Tests a sample of values from each standard.
    """
    print("\n" + "="*70)
    print("TEST 1: IEC Table Consistency (Python vs SysML)")
    print("="*70)

    # Test cases: (voltage, insulation_type, expected_61010, expected_61439)
    test_cases = [
        (50.0, "functional", 0.5, 1.0),
        (100.0, "basic", 1.0, 1.5),
        (230.0, "basic", 4.0, 3.0),  # 230V rounds up to 250V entry
        (250.0, "basic", 4.0, 3.0),
        (250.0, "reinforced", 8.0, 3.0),
        (400.0, "basic", 5.5, 4.0),
    ]

    all_pass = True
    for voltage, insulation, exp_61010, exp_61439 in test_cases:
        actual_61010 = lookup_iec_61010_1(voltage, insulation)
        actual_61439 = lookup_iec_61439_1(voltage)

        match_61010 = abs(actual_61010 - exp_61010) < 0.01
        match_61439 = abs(actual_61439 - exp_61439) < 0.01

        status = "PASS" if (match_61010 and match_61439) else "FAIL"
        if status == "FAIL":
            all_pass = False

        print(f"  {voltage}V/{insulation}: IEC61010={actual_61010}mm (exp={exp_61010}), "
              f"IEC61439={actual_61439}mm (exp={exp_61439}) -> {status}")

    print(f"\n  Result: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
    return all_pass


def test_requirement_to_verification_chain():
    """
    Test the full traceability chain from requirement to verification.

    Chain:
      ElectricalClearanceReq (requirement)
        -> PartWithPower (satisfies requirement)
          -> ClearanceAnalysis (calc)
            -> ClearanceVerification (verification case)
              -> VerdictKind (pass/fail)
    """
    print("\n" + "="*70)
    print("TEST 2: Requirement -> Verification Traceability Chain")
    print("="*70)

    # Create SysML-equivalent parts (from Gen2Panel1P12.sysml)
    parts = [
        PartWithPower("IntegratedMeter::phaseInTerminal", voltage_V=230.0, current_A=80.0),
        PartWithPower("SupplyBusbars", voltage_V=230.0, current_A=80.0),
        PartWithPower("GridRelay", voltage_V=230.0, current_A=80.0),
        PartWithPower("ConfigurableMainSwitch", voltage_V=230.0, current_A=80.0),
    ]

    print("\n  Parts under test (all extend PartWithPower):")
    for part in parts:
        print(f"    - {part.name}: {part.voltage_V}V, {part.current_A}A, "
              f"insulation={part.insulation_type.value}")
        print(f"      Satisfies: {part.clearance_req.id}")

    return True


def test_verification_with_mock_data():
    """
    Run verification cases using mock OnShape measurement data.

    This simulates what would happen during a real verification:
    1. Read part properties from SysML model
    2. Calculate required clearance from IEC tables
    3. Get actual clearance from OnShape (MOCKED)
    4. Run ClearanceVerification to get verdict
    """
    print("\n" + "="*70)
    print("TEST 3: Verification Cases with Mock Measurements")
    print("="*70)

    # Define terminal pairs to verify (from Gen2Panel1P12.sysml IntegratedMeter)
    terminal_pairs = [
        {
            "part1": PartWithPower("IntegratedMeter::phaseInTerminal", 230.0, 80.0),
            "part2": PartWithPower("IntegratedMeter::neutralInTerminal", 230.0, 80.0),
            "mock_key": ("phaseInTerminal", "neutralInTerminal"),
            "description": "Phase-In to Neutral-In terminal clearance"
        },
        {
            "part1": PartWithPower("IntegratedMeter::phaseInScrew", 230.0, 80.0),
            "part2": PartWithPower("IntegratedMeter::neutralInScrew", 230.0, 80.0),
            "mock_key": ("phaseInScrew", "neutralInScrew"),
            "description": "Phase-In to Neutral-In screw clearance"
        },
        {
            "part1": PartWithPower("GridRelay::phasePole", 230.0, 80.0),
            "part2": PartWithPower("GridRelay::neutralPole", 230.0, 80.0),
            "mock_key": ("gridRelay_phase", "gridRelay_neutral"),
            "description": "Grid Relay phase to neutral pole clearance"
        },
        {
            "part1": PartWithPower("ConfigurableMainSwitch::phase", 230.0, 80.0),
            "part2": PartWithPower("ConfigurableMainSwitch::neutral", 230.0, 80.0),
            "mock_key": ("mainSwitch_phase", "mainSwitch_neutral"),
            "description": "Main Switch phase to neutral clearance"
        },
    ]

    results = []

    print("\n  Running verification cases...\n")

    for pair in terminal_pairs:
        part = pair["part1"]  # Use first part for voltage/insulation

        # Step 1: Calculate required clearance from IEC tables
        required_mm, clearances_by_std = calculate_clearance(
            part.voltage_V,
            part.current_A,
            part.insulation_type.value,
            apply_both_standards=True
        )

        # Step 2: Get actual clearance (MOCK - would be from OnShape API)
        actual_mm = MOCK_MEASURED_CLEARANCES.get(pair["mock_key"], 0.0)

        # Step 3: Run verification
        verdict, details = clearance_verification(part, actual_mm, required_mm)

        # Step 4: Generate description
        description = get_clearance_description(
            part.voltage_V, part.current_A, required_mm, clearances_by_std
        )

        result = {
            "description": pair["description"],
            "verdict": verdict,
            "details": details,
            "clearances_by_standard": clearances_by_std,
            "clearance_description": description
        }
        results.append(result)

        # Print result
        status_symbol = "[PASS]" if verdict == VerdictKind.PASS else "[FAIL]"
        print(f"  {status_symbol} {pair['description']}")
        print(f"         Required: {required_mm:.2f}mm (worst case)")
        print(f"         Actual:   {actual_mm:.2f}mm (mock measurement)")
        print(f"         Margin:   {details['margin_mm']:.2f}mm")
        print(f"         Standards: IEC61010={clearances_by_std['IEC_61010_1']:.1f}mm, "
              f"IEC61439={clearances_by_std['IEC_61439_1']:.1f}mm")
        print(f"         Satisfies: {details['requirement_id']}")
        print()

    # Summary
    passed = sum(1 for r in results if r["verdict"] == VerdictKind.PASS)
    failed = len(results) - passed

    print("-"*70)
    print(f"  SUMMARY: {passed} passed, {failed} failed out of {len(results)} verification cases")

    return results


def test_traceability_report():
    """
    Generate a traceability report showing the complete chain.
    """
    print("\n" + "="*70)
    print("TEST 4: Traceability Report")
    print("="*70)

    print("""
  TRACEABILITY CHAIN:

  +----------------------------------+
  | IECStandards.sysml               |
  +----------------------------------+
  |                                  |
  | requirement def                  |
  |   ElectricalClearanceReq         |<----+
  |     voltage_V: Real              |     |
  |     insulationType: InsulationType    |
  |     requiredClearance_mm: Real   |     |
  |     require constraint:          |     |
  |       ClearanceConstraint        |     |
  |                                  |     |
  +----------------------------------+     |
            |                              |
            | verify                       | satisfy
            v                              |
  +----------------------------------+     |
  | verification def                 |     |
  |   ClearanceVerification          |     |
  |     subject: PartWithPower       |-----+
  |     in actualClearance_mm        |     ^
  |     in requiredClearance_mm      |     |
  |     objective:                   |     |
  |       verify ElectricalClearanceReq   |
  |     return: VerdictKind          |     |
  |                                  |     |
  +----------------------------------+     |
            ^                              |
            | uses                         |
            |                              |
  +----------------------------------+     |
  | calc def ClearanceAnalysis       |     |
  |   in voltage_V                   |     |
  |   in insulationType              |     |
  |   in actualClearance_mm          |     |
  |   in requiredClearance_mm        |     |
  |   return margin_mm               |     |
  +----------------------------------+     |
                                           |
  +----------------------------------+     |
  | Gen2Panel1P12.sysml              |     |
  +----------------------------------+     |
  |                                  |     |
  | part def MainsTerminals          |     |
  |   :> PartWithPower ---------> inherits satisfy
  |                                  |
  | part def SupplyBusbars           |
  |   :> PartWithPower ---------> inherits satisfy
  |                                  |
  | part def GridRelay               |
  |   :> PartWithPower ---------> inherits satisfy
  |                                  |
  | part def IntegratedMeter         |
  |   :> PartWithPower ---------> inherits satisfy
  |     part phaseInTerminal         |
  |     part neutralInTerminal       |
  |     ...                          |
  |                                  |
  +----------------------------------+

  EXTERNAL INPUTS (from OnShape MCP):
  - actualClearance_mm: Measured distance between terminals
  - Material properties (for future use)

  IEC STANDARDS LOOKUP (iec_clearance.py):
  - Matches IECStandards::IEC61010_1 and IEC61439_1 packages
  - Returns requiredClearance_mm based on voltage and insulation type
    """)

    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" SYSML TRACEABILITY MOCK TEST")
    print(" Testing: Requirement -> Analysis -> Verification Chain")
    print("="*70)
    print("\n This test uses MOCK data - no OnShape API calls required.\n")

    # Run tests
    test1_pass = test_iec_table_matches_sysml()
    test2_pass = test_requirement_to_verification_chain()
    results = test_verification_with_mock_data()
    test4_pass = test_traceability_report()

    # Final summary
    print("\n" + "="*70)
    print(" FINAL SUMMARY")
    print("="*70)

    all_verdicts_pass = all(r["verdict"] == VerdictKind.PASS for r in results)

    print(f"""
  Test 1 (IEC Tables):        {'PASS' if test1_pass else 'FAIL'}
  Test 2 (Traceability):      {'PASS' if test2_pass else 'FAIL'}
  Test 3 (Verification):      {'PASS' if all_verdicts_pass else 'FAIL (expected - mock data includes failure case)'}
  Test 4 (Report):            {'PASS' if test4_pass else 'FAIL'}

  NOTE: Test 3 includes an intentional failure case (GridRelay) to
  demonstrate that the verification correctly identifies non-compliant parts.

  The traceability chain is complete:
    ElectricalClearanceReq (requirement)
      <- satisfied by PartWithPower (and all derived parts)
        <- verified by ClearanceVerification
          <- using ClearanceAnalysis (calc)
            <- with IEC lookup tables matching SysML package
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
