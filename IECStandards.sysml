/**
 * IEC Electrical Clearance Standards Package
 *
 * Contains clearance requirements from:
 * - IEC 61010-1: Safety requirements for electrical equipment for measurement, control, and laboratory use
 * - IEC 61439-1: Low-voltage switchgear and controlgear assemblies
 *
 * Values represent minimum air clearance distances in millimeters.
 */
package IECStandards {
    private import ScalarValues::Real;
    private import ScalarValues::Boolean;
    private import VerificationCases::VerdictKind;

    // =========================================================
    // Insulation Type Enumeration
    // =========================================================

    enum def InsulationType {
        functional;   // Basic operational insulation
        basic;        // Single level of protection
        reinforced;   // Double basic insulation (2x protection)
    }

    // =========================================================
    // Attribute Definitions
    // =========================================================

    attribute def ClearanceEntry {
        attribute voltage_V : Real;           // Voltage in Volts
        attribute insulationType : InsulationType;
        attribute clearance_mm : Real;        // Clearance in millimeters
    }

    // =========================================================
    // IEC 61010-1 Clearance Requirements
    // Safety requirements for measurement equipment
    // =========================================================

    package IEC61010_1 {
        doc /*
         * IEC 61010-1: Safety requirements for electrical equipment
         * for measurement, control, and laboratory use.
         * Clearance values depend on voltage AND insulation type.
         */

        // Functional Insulation Clearances
        package FunctionalInsulation {
            attribute clearance_50V : ClearanceEntry {
                :>> voltage_V = 50.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 0.5;
            }
            attribute clearance_100V : ClearanceEntry {
                :>> voltage_V = 100.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 1.0;
            }
            attribute clearance_150V : ClearanceEntry {
                :>> voltage_V = 150.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 1.5;
            }
            attribute clearance_200V : ClearanceEntry {
                :>> voltage_V = 200.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 2.0;
            }
            attribute clearance_250V : ClearanceEntry {
                :>> voltage_V = 250.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 3.0;
            }
            attribute clearance_300V : ClearanceEntry {
                :>> voltage_V = 300.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 3.5;
            }
            attribute clearance_400V : ClearanceEntry {
                :>> voltage_V = 400.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 4.0;
            }
            attribute clearance_500V : ClearanceEntry {
                :>> voltage_V = 500.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 5.0;
            }
            attribute clearance_600V : ClearanceEntry {
                :>> voltage_V = 600.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 6.0;
            }
            attribute clearance_800V : ClearanceEntry {
                :>> voltage_V = 800.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 8.0;
            }
            attribute clearance_1000V : ClearanceEntry {
                :>> voltage_V = 1000.0;
                :>> insulationType = InsulationType::functional;
                :>> clearance_mm = 10.0;
            }
        }

        // Basic Insulation Clearances
        package BasicInsulation {
            attribute clearance_50V : ClearanceEntry {
                :>> voltage_V = 50.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 0.5;
            }
            attribute clearance_100V : ClearanceEntry {
                :>> voltage_V = 100.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 1.0;
            }
            attribute clearance_150V : ClearanceEntry {
                :>> voltage_V = 150.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 1.5;
            }
            attribute clearance_200V : ClearanceEntry {
                :>> voltage_V = 200.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 2.0;
            }
            attribute clearance_250V : ClearanceEntry {
                :>> voltage_V = 250.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 4.0;
            }
            attribute clearance_300V : ClearanceEntry {
                :>> voltage_V = 300.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 4.5;
            }
            attribute clearance_400V : ClearanceEntry {
                :>> voltage_V = 400.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 5.5;
            }
            attribute clearance_500V : ClearanceEntry {
                :>> voltage_V = 500.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 6.5;
            }
            attribute clearance_600V : ClearanceEntry {
                :>> voltage_V = 600.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 8.0;
            }
            attribute clearance_800V : ClearanceEntry {
                :>> voltage_V = 800.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 10.0;
            }
            attribute clearance_1000V : ClearanceEntry {
                :>> voltage_V = 1000.0;
                :>> insulationType = InsulationType::basic;
                :>> clearance_mm = 12.0;
            }
        }

        // Reinforced Insulation Clearances (Double Basic)
        package ReinforcedInsulation {
            attribute clearance_50V : ClearanceEntry {
                :>> voltage_V = 50.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 1.0;
            }
            attribute clearance_100V : ClearanceEntry {
                :>> voltage_V = 100.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 2.0;
            }
            attribute clearance_150V : ClearanceEntry {
                :>> voltage_V = 150.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 3.0;
            }
            attribute clearance_200V : ClearanceEntry {
                :>> voltage_V = 200.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 4.0;
            }
            attribute clearance_250V : ClearanceEntry {
                :>> voltage_V = 250.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 8.0;
            }
            attribute clearance_300V : ClearanceEntry {
                :>> voltage_V = 300.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 9.0;
            }
            attribute clearance_400V : ClearanceEntry {
                :>> voltage_V = 400.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 11.0;
            }
            attribute clearance_500V : ClearanceEntry {
                :>> voltage_V = 500.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 13.0;
            }
            attribute clearance_600V : ClearanceEntry {
                :>> voltage_V = 600.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 16.0;
            }
            attribute clearance_800V : ClearanceEntry {
                :>> voltage_V = 800.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 20.0;
            }
            attribute clearance_1000V : ClearanceEntry {
                :>> voltage_V = 1000.0;
                :>> insulationType = InsulationType::reinforced;
                :>> clearance_mm = 24.0;
            }
        }
    }

    // =========================================================
    // IEC 61439-1 Clearance Requirements
    // Low-voltage switchgear and controlgear assemblies
    // =========================================================

    package IEC61439_1 {
        doc /*
         * IEC 61439-1: Low-voltage switchgear and controlgear assemblies.
         * Clearance values depend on voltage only.
         */

        attribute clearance_50V : ClearanceEntry {
            :>> voltage_V = 50.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 1.0;
        }
        attribute clearance_100V : ClearanceEntry {
            :>> voltage_V = 100.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 1.5;
        }
        attribute clearance_150V : ClearanceEntry {
            :>> voltage_V = 150.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 2.0;
        }
        attribute clearance_200V : ClearanceEntry {
            :>> voltage_V = 200.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 2.5;
        }
        attribute clearance_250V : ClearanceEntry {
            :>> voltage_V = 250.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 3.0;
        }
        attribute clearance_300V : ClearanceEntry {
            :>> voltage_V = 300.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 3.5;
        }
        attribute clearance_400V : ClearanceEntry {
            :>> voltage_V = 400.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 4.0;
        }
        attribute clearance_500V : ClearanceEntry {
            :>> voltage_V = 500.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 5.0;
        }
        attribute clearance_600V : ClearanceEntry {
            :>> voltage_V = 600.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 6.0;
        }
        attribute clearance_800V : ClearanceEntry {
            :>> voltage_V = 800.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 8.0;
        }
        attribute clearance_1000V : ClearanceEntry {
            :>> voltage_V = 1000.0;
            :>> insulationType = InsulationType::basic;
            :>> clearance_mm = 10.0;
        }
    }

    // =========================================================
    // Constraint Definitions for Clearance Verification
    // =========================================================

    constraint def ClearanceConstraint {
        doc /* Verifies that actual clearance meets or exceeds required clearance */

        in actualClearance_mm : Real;
        in requiredClearance_mm : Real;

        actualClearance_mm >= requiredClearance_mm
    }

    constraint def WorstCaseClearanceConstraint {
        doc /*
         * Verifies clearance against worst case (maximum) requirement
         * from both IEC 61010-1 and IEC 61439-1 standards.
         */

        in actualClearance_mm : Real;
        in iec61010Clearance_mm : Real;
        in iec61439Clearance_mm : Real;

        actualClearance_mm >= iec61010Clearance_mm and actualClearance_mm >= iec61439Clearance_mm
    }

    // =========================================================
    // Requirement Definitions
    // =========================================================

    requirement def ElectricalClearanceReq {
        doc /*
         * Electrical parts shall meet minimum clearance requirements
         * based on voltage and current ratings per IEC 61010-1 and
         * IEC 61439-1 standards. Worst case (maximum) clearance is
         * selected from both standards.
         */

        attribute voltage_V : Real;
        attribute insulationType : InsulationType;
        attribute requiredClearance_mm : Real;

        require constraint : ClearanceConstraint;
    }

    // =========================================================
    // Analysis Definition - Calculates clearance margin
    // =========================================================

    calc def ClearanceAnalysis {
        doc /*
         * Analyzes electrical clearance by comparing actual measured
         * clearance against required clearance from IEC standards.
         * Returns the margin (positive = compliant, negative = violation).
         *
         * Inputs:
         *   - voltage_V: Operating voltage
         *   - insulationType: Type of insulation
         *   - actualClearance_mm: Measured clearance from CAD (external input)
         *   - requiredClearance_mm: Required clearance from IEC tables
         *
         * Outputs:
         *   - margin_mm: Difference between actual and required
         */

        in voltage_V : Real;
        in insulationType : InsulationType;
        in actualClearance_mm : Real;      // Provided externally (e.g., from OnShape)
        in requiredClearance_mm : Real;    // From IEC lookup tables

        // Output: margin (positive = pass, negative = fail)
        return margin_mm : Real = actualClearance_mm - requiredClearance_mm;
    }

    calc def IsCompliant {
        doc /* Returns true if margin is non-negative (clearance requirement met) */

        in margin_mm : Real;
        return : Boolean = margin_mm >= 0.0;
    }

    // =========================================================
    // Verification Definition - Formal V&V traceability
    // =========================================================

    verification def ClearanceVerification {
        doc /*
         * Verification case for electrical clearance requirements.
         * Links to ElectricalClearanceReq for formal traceability.
         *
         * Verification method: External measurement via CAD system (OnShape)
         * with comparison against IEC 61010-1 and IEC 61439-1 lookup tables.
         *
         * Inputs (provided at verification time):
         *   - actualClearance_mm: Measured clearance from CAD
         *   - requiredClearance_mm: Required clearance from IEC lookup
         *
         * Returns: VerdictKind (pass if actual >= required, fail otherwise)
         */

        subject partUnderTest : PartWithPower;

        // External inputs provided at verification time
        in actualClearance_mm : Real;      // Measured from CAD
        in requiredClearance_mm : Real;    // From IEC lookup

        objective clearanceObjective {
            doc /* Verify that the part meets electrical clearance requirements */
            verify requirement : ElectricalClearanceReq;
        }

        // Verification passes if actual clearance meets or exceeds required
        return verdict : VerdictKind =
            if actualClearance_mm >= requiredClearance_mm ? VerdictKind::pass else VerdictKind::fail;
    }

    // =========================================================
    // Abstract Part Definition for Powered Components
    // =========================================================

    abstract part def PartWithPower {
        doc /*
         * Abstract base for any part that carries electrical power
         * and must satisfy clearance requirements.
         */

        attribute voltage_V : Real default 230.0;
        attribute current_A : Real default 80.0;
        attribute insulationType : InsulationType default InsulationType::basic;

        // All powered parts must satisfy clearance requirement
        satisfy requirement clearanceReq : ElectricalClearanceReq {
            :>> voltage_V = PartWithPower::voltage_V;
            :>> insulationType = PartWithPower::insulationType;
        }
    }
}
