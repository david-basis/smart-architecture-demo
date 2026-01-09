"""IEC clearance standards lookup tables and calculations."""

from typing import Dict, Tuple, Optional


# IEC 61010-1 (Measurement Equipment) Clearance Table
# Values in millimeters
IEC_61010_1_CLEARANCE: Dict[Tuple[float, str], float] = {
    # (voltage, insulation_type) -> clearance_mm
    # Functional insulation
    (50.0, "functional"): 0.5,
    (100.0, "functional"): 1.0,
    (150.0, "functional"): 1.5,
    (200.0, "functional"): 2.0,
    (250.0, "functional"): 3.0,
    (300.0, "functional"): 3.5,
    (400.0, "functional"): 4.0,
    (500.0, "functional"): 5.0,
    (600.0, "functional"): 6.0,
    (800.0, "functional"): 8.0,
    (1000.0, "functional"): 10.0,
    
    # Basic insulation
    (50.0, "basic"): 0.5,
    (100.0, "basic"): 1.0,
    (150.0, "basic"): 1.5,
    (200.0, "basic"): 2.0,
    (250.0, "basic"): 4.0,
    (300.0, "basic"): 4.5,
    (400.0, "basic"): 5.5,
    (500.0, "basic"): 6.5,
    (600.0, "basic"): 8.0,
    (800.0, "basic"): 10.0,
    (1000.0, "basic"): 12.0,
    
    # Reinforced insulation (double basic)
    (50.0, "reinforced"): 1.0,
    (100.0, "reinforced"): 2.0,
    (150.0, "reinforced"): 3.0,
    (200.0, "reinforced"): 4.0,
    (250.0, "reinforced"): 8.0,
    (300.0, "reinforced"): 9.0,
    (400.0, "reinforced"): 11.0,
    (500.0, "reinforced"): 13.0,
    (600.0, "reinforced"): 16.0,
    (800.0, "reinforced"): 20.0,
    (1000.0, "reinforced"): 24.0,
}

# IEC 61439-1 (Low-voltage switchgear) Clearance Table
# Values in millimeters
IEC_61439_1_CLEARANCE: Dict[float, float] = {
    # voltage -> clearance_mm
    50.0: 1.0,
    100.0: 1.5,
    150.0: 2.0,
    200.0: 2.5,
    250.0: 3.0,
    300.0: 3.5,
    400.0: 4.0,
    500.0: 5.0,
    600.0: 6.0,
    800.0: 8.0,
    1000.0: 10.0,
}


def lookup_iec_61010_1(voltage: float, insulation_type: str = "basic") -> float:
    """
    Lookup clearance from IEC 61010-1 table.
    
    Args:
        voltage: Voltage in volts
        insulation_type: "functional", "basic", or "reinforced"
        
    Returns:
        Clearance in millimeters
    """
    # Find closest voltage match
    voltage_keys = sorted([v for v, _ in IEC_61010_1_CLEARANCE.keys() if _ == insulation_type])
    
    if not voltage_keys:
        return 0.0
    
    # Find matching or next higher voltage
    for v in voltage_keys:
        if voltage <= v:
            return IEC_61010_1_CLEARANCE[(v, insulation_type)]
    
    # If voltage exceeds table, use highest value
    max_v = max(voltage_keys)
    return IEC_61010_1_CLEARANCE[(max_v, insulation_type)]


def lookup_iec_61439_1(voltage: float) -> float:
    """
    Lookup clearance from IEC 61439-1 table.
    
    Args:
        voltage: Voltage in volts
        
    Returns:
        Clearance in millimeters
    """
    # Find closest voltage match
    voltage_keys = sorted(IEC_61439_1_CLEARANCE.keys())
    
    # Find matching or next higher voltage
    for v in voltage_keys:
        if voltage <= v:
            return IEC_61439_1_CLEARANCE[v]
    
    # If voltage exceeds table, use highest value
    max_v = max(voltage_keys)
    return IEC_61439_1_CLEARANCE[max_v]


def calculate_clearance(
    voltage: float,
    current: float = 0.0,
    insulation_type: str = "basic",
    apply_both_standards: bool = True
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate required clearance using IEC standards.
    Returns worst case (maximum) clearance requirement.
    
    Args:
        voltage: Voltage in volts
        current: Current in amperes (for future use)
        insulation_type: "functional", "basic", or "reinforced" (IEC 61010-1)
        apply_both_standards: If True, check both IEC 61010-1 and IEC 61439-1
        
    Returns:
        Tuple of (worst_case_clearance_mm, {standard: clearance_mm})
    """
    clearances = {}
    
    # IEC 61010-1
    clearance_61010 = lookup_iec_61010_1(voltage, insulation_type)
    clearances["IEC_61010_1"] = clearance_61010
    
    # IEC 61439-1
    if apply_both_standards:
        clearance_61439 = lookup_iec_61439_1(voltage)
        clearances["IEC_61439_1"] = clearance_61439
    else:
        clearance_61439 = 0.0
    
    # Return worst case (maximum)
    worst_case = max(clearance_61010, clearance_61439)
    
    return worst_case, clearances


def get_clearance_description(
    voltage: float,
    current: float,
    clearance_mm: float,
    clearances: Dict[str, float]
) -> str:
    """
    Generate description for clearance requirement.
    
    Args:
        voltage: Voltage in volts
        current: Current in amperes
        clearance_mm: Required clearance in millimeters
        clearances: Dictionary of clearances by standard
        
    Returns:
        Description string
    """
    desc = f"Minimum clearance: {clearance_mm:.2f}mm for {voltage}V, {current}A"
    
    if len(clearances) > 1:
        standards = []
        for std, val in clearances.items():
            standards.append(f"{std}: {val:.2f}mm")
        desc += f" (worst case of: {', '.join(standards)})"
    else:
        std_name = list(clearances.keys())[0]
        desc += f" (per {std_name})"
    
    return desc
