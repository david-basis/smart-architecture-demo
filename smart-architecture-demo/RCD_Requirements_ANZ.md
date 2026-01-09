# RCD Requirements for Gen2Panel - ANZ Markets

## Document Information
- **System**: Gen2Panel1P12 (Single-Phase, 2-Circuit Panel)
- **Target Markets**: Australia and New Zealand
- **Standards**: AS/NZS 3000:2018, AS/NZS 61008, AS/NZS 61009
- **Date**: 2024

---

## 1. Standards Compliance Requirements

### 1.1 Device Standards
**REQ-RCD-001**: The RCD device shall comply with AS/NZS 61008 (RCCB) or AS/NZS 61009 (RCBO) as applicable.

**REQ-RCD-002**: The RCD shall be rated for operation at:
- Rated voltage: Up to 440 V AC (single-phase)
- Rated current: Up to 125 A (as per system design)
- Rated short-circuit capacity: Up to 25,000 A (for RCBOs)

**REQ-RCD-003**: The RCD shall be designed for use in environments with pollution degree 2.

### 1.2 Installation Standards
**REQ-RCD-004**: The system shall comply with AS/NZS 3000:2018 Wiring Rules for RCD protection requirements.

**REQ-RCD-005**: All final sub-circuits (load01, load02) shall be protected by RCDs with a rated residual operating current not exceeding 30 mA.

---

## 2. Functional Requirements

### 2.1 Main Switch RCD Protection
**REQ-RCD-006**: The ConfigurableMainSwitch shall incorporate an RCDCircuit that provides upstream protection for all downstream circuits.

**REQ-RCD-007**: The main switch RCD shall be configurable to operate as either:
- Type AC (for general applications)
- Type A (for circuits with electronic equipment)
- Type S (Selective - time-delayed for coordination with downstream RCDs)

**REQ-RCD-008**: When Type S (selective) RCD is configured, it shall have a time delay sufficient to allow downstream RCDs to trip first, preventing unnecessary disconnection of multiple circuits.

### 2.2 Circuit-Level RCD Protection
**REQ-RCD-009**: Each CircuitModule (c01, c02) shall incorporate an RCDSensor that monitors residual current for its respective circuit.

**REQ-RCD-010**: Circuit-level RCD protection shall operate independently for each circuit, allowing selective disconnection of faulted circuits only.

**REQ-RCD-011**: The RCDSensor in each CircuitModule shall detect residual current imbalances between phase and neutral conductors.

### 2.3 RCD Coordination
**REQ-RCD-012**: The system shall implement proper RCD coordination such that:
- Downstream circuit RCDs trip before upstream main switch RCD
- A fault on one circuit does not cause unnecessary disconnection of other circuits
- The main switch RCD provides backup protection if circuit-level RCDs fail

**REQ-RCD-013**: The SystemManager shall monitor and coordinate RCD operation across all circuits via the T1S communication bus.

---

## 3. Performance Requirements

### 3.1 Sensitivity
**REQ-RCD-014**: The rated residual operating current (IΔn) shall be 30 mA for all RCDs protecting final sub-circuits.

**REQ-RCD-015**: The main switch RCD may have a higher sensitivity rating (e.g., 30 mA, 100 mA, or 300 mA) when configured as Type S, provided it does not compromise downstream protection.

**REQ-RCD-016**: The RCD shall trip within the following time limits at rated residual current:
- Type AC/A: ≤ 0.3 seconds at IΔn
- Type S: ≤ 0.5 seconds at IΔn (with time delay)

### 3.2 Operating Characteristics
**REQ-RCD-017**: The RCD shall not trip at residual currents below 50% of IΔn (half the rated sensitivity).

**REQ-RCD-018**: The RCD shall trip reliably at residual currents between 50% and 100% of IΔn.

**REQ-RCD-019**: The RCD shall trip within 0.04 seconds at residual currents ≥ 5 × IΔn.

### 3.3 Frequency Response
**REQ-RCD-020**: Type AC RCDs shall operate correctly at 50 Hz ± 2% (ANZ standard frequency).

**REQ-RCD-021**: Type A RCDs shall detect both sinusoidal AC residual currents and pulsating DC residual currents.

---

## 4. Safety Requirements

### 4.1 Protection Against Electric Shock
**REQ-RCD-022**: The RCD shall provide protection against:
- Direct contact (additional protection)
- Indirect contact (fault protection)
- Earth fault currents

**REQ-RCD-023**: The RCD shall disconnect all live conductors (phase and neutral) when a residual current fault is detected.

**REQ-RCD-024**: The RCD shall maintain protection even in the event of neutral conductor failure upstream of the RCD.

### 4.2 Overcurrent Coordination
**REQ-RCD-025**: When RCBOs are used, the overcurrent protection shall coordinate with the circuit breaker characteristics to prevent nuisance tripping.

**REQ-RCD-026**: The RCD shall not be damaged by short-circuit currents up to the rated short-circuit capacity.

### 4.3 Isolation
**REQ-RCD-027**: When the RCD trips, it shall provide full isolation of the protected circuit(s) with visible indication of the tripped state.

**REQ-RCD-028**: The RCD shall require manual reset after tripping; automatic re-closing shall not be permitted.

---

## 5. Testing and Verification Requirements

### 5.1 Test Button Functionality
**REQ-RCD-029**: The ConfigurableMainSwitch shall incorporate a TestButton that allows manual testing of the RCD functionality.

**REQ-RCD-030**: The test button shall simulate a residual current fault sufficient to trip the RCD when pressed.

**REQ-RCD-031**: The test button shall be easily accessible and clearly labeled as per AS/NZS 3000:2018 requirements.

**REQ-RCD-032**: The test button operation shall be indicated via the StatusLED and/or EInkDisplay.

### 5.2 Self-Testing
**REQ-RCD-033**: The RCDCircuit shall perform periodic self-tests to verify functionality (if electronic RCD type).

**REQ-RCD-034**: Self-test failures shall be indicated via the StatusPort and communicated to the SystemManager via T1S bus.

**REQ-RCD-035**: The system shall log RCD test events and trip events for diagnostic purposes.

### 5.3 Verification Tests
**REQ-RCD-036**: The RCD shall pass all verification tests specified in AS/NZS 61008 or AS/NZS 61009, including:
- Dielectric tests
- Temperature rise tests
- Short-circuit tests
- Residual current operating tests
- Mechanical endurance tests

---

## 6. Installation and Configuration Requirements

### 6.1 Circuit Distribution
**REQ-RCD-037**: The system shall support a minimum of 2 RCDs (as required by AS/NZS 3000:2018 for multiple circuits).

**REQ-RCD-038**: No more than 3 final sub-circuits shall be protected by a single RCD (current system has 2 circuits, which is compliant).

**REQ-RCD-039**: If the system is expanded beyond 2 circuits, lighting circuits shall be distributed across different RCDs to minimize impact of single RCD tripping.

### 6.2 Labeling and Identification
**REQ-RCD-040**: All RCDs shall be clearly labeled with:
- Rated residual operating current (IΔn)
- RCD type (AC, A, S)
- Test button location
- Protected circuit identification

**REQ-RCD-041**: The EInkDisplay on the ConfigurableMainSwitch shall display RCD status and configuration information.

### 6.3 Neutral Conductor Requirements
**REQ-RCD-042**: The RCD shall monitor both phase and neutral conductors; the neutral shall pass through the RCD and be switched/disconnected on trip.

**REQ-RCD-043**: The system architecture shall ensure that neutral conductors are properly routed through RCD sensing elements in both the main switch and circuit modules.

---

## 7. Communication and Monitoring Requirements

### 7.1 Status Reporting
**REQ-RCD-044**: The RCDCircuit shall report its status (normal, tripped, fault) via the StatusPort to the SystemManager.

**REQ-RCD-045**: Each CircuitModule RCDSensor shall report residual current measurements and trip status via the T1S bus.

**REQ-RCD-046**: The SystemManager shall aggregate RCD status information and make it available via the DataPort (WAN interface) for remote monitoring.

### 7.2 Event Logging
**REQ-RCD-047**: The system shall log all RCD trip events with timestamp, circuit identification, and residual current magnitude (if available).

**REQ-RCD-048**: The system shall maintain a history of RCD test button operations and self-test results.

---

## 8. Environmental and Reliability Requirements

### 8.1 Operating Environment
**REQ-RCD-049**: The RCD shall operate reliably in ambient temperatures from -5°C to +40°C (standard switchboard environment).

**REQ-RCD-050**: The RCD shall maintain performance characteristics over its operational lifetime (minimum 10,000 operations or 20 years, whichever comes first).

### 8.2 Immunity
**REQ-RCD-051**: The RCD shall be immune to:
- Voltage transients (surge protection provided by SPD)
- Electromagnetic interference
- Power supply variations within ±10% of nominal voltage

**REQ-RCD-052**: The RCD shall not cause nuisance tripping due to normal load switching or inrush currents.

---

## 9. Special Applications

### 9.1 Medical Installations
**REQ-RCD-053**: For medical installations or medical equipment, the system shall support configuration with 10 mA RCDs with switched neutral capability (per AS/NZS 3003).

### 9.2 DER Integration
**REQ-RCD-054**: The RCD protection shall remain effective when the system is operating in island mode (grid relay open) with DER sources connected.

**REQ-RCD-055**: The RCD shall detect residual current faults regardless of power flow direction (grid import or DER export).

---

## 10. Documentation Requirements

### 10.1 Technical Documentation
**REQ-RCD-056**: The system shall be supplied with documentation that includes:
- RCD specifications and ratings
- Installation instructions per AS/NZS 3000:2018
- Test procedures and verification methods
- Maintenance requirements

### 10.2 Compliance Documentation
**REQ-RCD-057**: The system shall be supplied with evidence of compliance with AS/NZS 61008/61009, including test certificates from accredited testing laboratories.

**REQ-RCD-058**: Installation documentation shall reference applicable sections of AS/NZS 3000:2018.

---

## 11. System Architecture Compliance

### 11.1 Current System Analysis
The Gen2Panel1P12 system architecture includes:
- **ConfigurableMainSwitch** with RCDCircuit (upstream protection)
- **CircuitModule** (c01, c02) each with RCDSensor (circuit-level protection)

This architecture satisfies:
- ✅ Minimum 2 RCDs requirement (main switch + circuit-level sensors)
- ✅ 30 mA protection for final sub-circuits
- ✅ Independent circuit protection
- ✅ Test button functionality
- ✅ Status monitoring and communication

### 11.2 Recommendations
**REQ-RCD-059**: The RCDCircuit in ConfigurableMainSwitch should be configurable as Type S (selective) to coordinate with downstream circuit-level RCDs.

**REQ-RCD-060**: The RCDSensor components in CircuitModules should be capable of independent tripping via the RelayCircuit to disconnect individual circuits.

**REQ-RCD-061**: The system should support remote RCD testing via the SystemManager and WAN interface for maintenance purposes.

---

## Summary

This requirements document specifies 61 requirements for RCD protection in the Gen2Panel system for ANZ markets. The requirements cover:

1. **Standards Compliance** (5 requirements) - AS/NZS 61008/61009 and AS/NZS 3000:2018
2. **Functional Requirements** (8 requirements) - RCD operation and coordination
3. **Performance Requirements** (8 requirements) - Sensitivity, timing, frequency response
4. **Safety Requirements** (7 requirements) - Protection, isolation, coordination
5. **Testing Requirements** (8 requirements) - Test buttons, self-testing, verification
6. **Installation Requirements** (6 requirements) - Circuit distribution, labeling, neutral handling
7. **Communication Requirements** (5 requirements) - Status reporting, event logging
8. **Environmental Requirements** (4 requirements) - Operating conditions, immunity
9. **Special Applications** (3 requirements) - Medical, DER integration
10. **Documentation Requirements** (3 requirements) - Technical and compliance docs
11. **System Architecture** (3 requirements) - Analysis and recommendations

All requirements are traceable to ANZ electrical standards and regulations, ensuring the system will be compliant and safe for use in Australian and New Zealand markets.
