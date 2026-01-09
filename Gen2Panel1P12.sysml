package Gen2Panel1P12 {
    // =========================================================
    // Items (simple payload types for ports; no external libs)
    // =========================================================

    item def ACPhase;
    item def ACNeutral;
    item def ACEarth;

    item def DC24V;

    item def T1SFrame;     // 10BASE-T1S
    item def RS485Frame;   // DER interfaces (2x RS485)
    item def SPIFrame;     // Backplane SPI (UI)

    item def CtrlSignal;
    item def StatusSignal;

    item def DataFrame;    // e.g., LPWAN / Cellular abstraction

    // State machine events
    item def close_cmd;
    item def open_cmd;
    item def reset_cmd;
    item def success;
    item def failure;
    item def fault_detected;

    // =========================================================
    // Port definitions
    // =========================================================

    port def AC1PPort {
        inout item phase  : ACPhase;
        inout item neutral: ACNeutral;
        inout item earth  : ACEarth;
    }

    port def EarthPort {
        inout item earth : ACEarth;
    }

    port def PhasePort {
        inout item phase : ACPhase;
    }

    port def NeutralPort {
        inout item neutral : ACNeutral;
    }

    port def DC24Port {
        inout item dc24 : DC24V;
    }

    port def T1SPort {
        inout item t1sframe : T1SFrame;
    }

    port def RS485Port {
        inout item rs485frame : RS485Frame;
    }

    port def SPIPort {
        inout item spiframe : SPIFrame;
    }

    port def ControlPort {
        inout item signal : CtrlSignal;
    }

    port def StatusPort {
        inout item signal : StatusSignal;
    }

    port def DataPort {
        inout item dataframe : DataFrame;
    }

    // =========================================================
    // Sub-part definitions (used inside higher-level modules)
    // =========================================================

    part def ShuntBreaker;
    part def RCDSensor;
    part def VoltageSense;
    part def RelayCircuit;
    part def HWInterlock;
    part def RelayPole;

    part def EInkDisplay;
    part def StatusLED;
    part def TestButton;
    part def RCDCircuit;

    part def ControlPSU;
    part def BatteryBackup;

    part def SPD_MOV;
    part def SPD_GDT;
    part def SPD_NE;          // optional N-E SPD (modeled as present)

    // =========================================================
    // Requirement definitions for electrical clearance
    // =========================================================

    requirement def ElectricalClearanceReq {
        id = "REQ-ELECTRICAL-CLEARANCE-001";
        text = "Electrical parts shall meet minimum clearance requirements based on voltage and current ratings per IEC 61010-1 and IEC 61439-1 standards. Worst case (maximum) clearance is selected from both standards.";
    }

    // =========================================================
    // Physical terminal definitions
    // =========================================================

    part def MeterTerminal {
        // Physical terminal for busbar connection
        // 
        // Attributes (managed via onshape_part_mapping.json):
        // - voltage: Real (default 230.0 V) - Electrical voltage rating
        // - current: Real (default 80.0 A) - Electrical current rating
        // - material: String (synced from OnShape dynamically) - Material type
        // - minClearance: Real (calculated from voltage/current per IEC standards) - Minimum clearance in mm
        //
        // Satisfies:
        // - ElectricalClearanceReq: Clearance verification per IEC standards
    }

    // =========================================================
    // Key subsystem definitions
    // =========================================================

    part def MainsTerminals {
        port phaseIn   : PhasePort;   // Phase terminal input
        port phaseOut  : PhasePort;   // Phase terminal output
        port neutralIn : NeutralPort; // Neutral terminal input
        port neutralOut: NeutralPort; // Neutral terminal output
        port earthIn   : EarthPort;   // Earth terminal input
        port earthOut  : EarthPort;   // Earth terminal output
    }

    part def SupplyBusbars {
        port phaseIn  : PhasePort;   // Phase input (from grid relay)
        port phaseOut : PhasePort;   // Phase output (to circuits)
        port neutralIn  : NeutralPort; // Neutral input (from grid relay)
        port neutralOut : NeutralPort; // Neutral output (to circuits)
    }

    part def EarthBusbar {
        port earth : EarthPort;  // Earth busbar for distribution
    }

    part def SurgeProtectionDevice {
        port phaseIn  : PhasePort;   // Phase input
        port phaseOut : PhasePort;   // Phase output
        port neutralIn  : NeutralPort; // Neutral input
        port neutralOut : NeutralPort; // Neutral output
        port earth    : EarthPort;   // Earth connection (L->E and N->E shunting)
        port status : StatusPort;

        part mov : SPD_MOV[1];  // L-N cartridge
        part gdt : SPD_GDT[1];  // Combined GDT and N-E: shunts L->E and N->E
    }

    part def PowerModule {
        port phaseIn  : PhasePort;
        port neutralIn : NeutralPort;
        port earth   : EarthPort;
        port dc24Out : DC24Port;

        port t1s : T1SPort;

        part controlPSU    : ControlPSU[1];
        part batteryBackup : BatteryBackup[1];
    }

    part def Backplane {
        port dc24In    : DC24Port;

        port t1sBus    : T1SPort;
        port t1sSpare  : T1SPort;

        port spi       : SPIPort;
    }

    part def IntegratedMeter {
        port phaseIn  : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn  : NeutralPort;  // Neutral shunt (pass-through, no physical terminal)
        port earth    : EarthPort;

        port t1s      : T1SPort;
        port status   : StatusPort;

        port wan      : DataPort;

        // Physical terminals for busbar connections
        part phaseInTerminal  : MeterTerminal[1];
        part phaseOutTerminal : MeterTerminal[1];
        part neutralInTerminal  : MeterTerminal[1];

        // Physical screws for terminal connections
        part phaseInScrew  : MeterTerminal[1];
        part phaseOutScrew : MeterTerminal[1];
        part neutralInScrew : MeterTerminal[1];

        // Allocation: logical ports to physical terminals
        // phaseIn allocated to phaseInTerminal
        // phaseOut allocated to phaseOutTerminal
        // neutralIn allocated to neutralInTerminal
        // Note: neutralOut is a logical pass-through only, no physical terminal
        // Screws are allocated to terminals (phaseInScrew -> phaseInTerminal, etc.)
    }

    part def SystemManager {
        port t1s      : T1SPort;

        port derA     : RS485Port;
        port derB     : RS485Port;

        port ctrlMainSwitch : ControlPort;
        port ctrlGridRelay  : ControlPort;

        port stsSpd    : StatusPort;
        port stsRelay  : StatusPort;

        port earth : EarthPort;
    }

    part def ConfigurableMainSwitch {
        port phaseIn   : PhasePort;
        port phaseOut  : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut: NeutralPort;
        port earth     : EarthPort;

        port ctrl  : ControlPort;
        port uiSpi : SPIPort;

        part rcdCircuit  : RCDCircuit[1];
        part testButton  : TestButton[1];
        part eInkDisplay : EInkDisplay[1];
        part statusLed   : StatusLED[1];
    }

    part def GridRelay {
        port phaseIn  : PhasePort;   // Phase only (neutral passes through separately)
        port phaseOut : PhasePort;
        port neutralIn  : NeutralPort; // Neutral pass-through
        port neutralOut : NeutralPort;
        port earth : EarthPort;

        port ctrl  : ControlPort;
        port status: StatusPort;

        part phasePole    : RelayPole[1];
        part neutralPole  : RelayPole[1];
        part hwInterlock  : HWInterlock[1];
        part shuntBreaker : ShuntBreaker[1];

        // =========================================================
        // GridRelay State Machine
        // =========================================================

        state def GridRelayStateMachine {
            entry; then OPEN;

            state OPEN {
                // Relay open, system isolated from grid (islanded)
                // Phase Pole: Open, Neutral Pole: Open (via hardware interlock)
                // Entry: Ensure both poles are open, report islanded status
                entry action enterOpenState {}
            }

            state CLOSING {
                // Transitioning from open to closed
                // Phase Pole: Closing, Neutral Pole: Closing (coordinated via hardware interlock)
                // Entry: Initiate closing sequence for both poles, start transition timeout timer
                entry action enterClosingState {}
            }

            state CLOSED {
                // Relay closed, system connected to grid
                // Phase Pole: Closed, Neutral Pole: Closed
                // Entry: Verify both poles closed, report grid-connected status
                entry action enterClosedState {}
            }

            state OPENING {
                // Transitioning from closed to open
                // Phase Pole: Opening, Neutral Pole: Opening (coordinated via hardware interlock)
                // Entry: Initiate opening sequence for both poles, start transition timeout timer
                entry action enterOpeningState {}
            }

            state FAULT {
                // Error state requiring attention
                // Phase Pole: Unknown/Unsafe, Neutral Pole: Unknown/Unsafe
                // Entry: Open both poles (fail-safe), report fault status, log fault condition
                entry action enterFaultState {}
            }

            transition t1
                first OPEN
                accept close_cmd
                then CLOSING;

            transition t2
                first CLOSING
                accept success
                then CLOSED;

            transition t3
                first CLOSING
                accept failure
                then OPEN;

            transition t4
                first CLOSED
                accept open_cmd
                then OPENING;

            transition t5
                first OPENING
                accept success
                then OPEN;

            transition t6
                first OPENING
                accept failure
                then FAULT;

            transition t7
                first OPEN
                accept fault_detected
                then FAULT;

            transition t8
                first CLOSING
                accept fault_detected
                then FAULT;

            transition t9
                first CLOSED
                accept fault_detected
                then FAULT;

            transition t10
                first OPENING
                accept fault_detected
                then FAULT;

            transition t11
                first FAULT
                accept reset_cmd
                then OPEN;
        }
    }

    part def CircuitModule {
        port phaseIn   : PhasePort;
        port phaseOut  : PhasePort;
        port neutralIn  : NeutralPort;
        port neutralOut : NeutralPort;
        port earth   : EarthPort;

        port t1s     : T1SPort;

        part shuntBreaker : ShuntBreaker[1];
        part rcdSensor    : RCDSensor[1];
        part voltageSense : VoltageSense[1];
        part relayCircuit : RelayCircuit[1];
    }

    part def Enclosure;

    // =========================================================
    // Top-level system (1P, 2 circuits)
    // =========================================================

    part def Gen2Panel {

        // External interfaces
        port phaseIn   : PhasePort;
        port neutralIn : NeutralPort;
        port earthIn   : EarthPort;

        port t1sExpansion : T1SPort;
        port derA         : RS485Port;
        port derB         : RS485Port;

        port load01 : AC1PPort;
        port load02 : AC1PPort;

        // Internal parts
        part mainsTerminals : MainsTerminals[1];
        part busbars    : SupplyBusbars[1];
        part earthBusbar : EarthBusbar[1];
        part spd        : SurgeProtectionDevice[1];
        part mainSwitch : ConfigurableMainSwitch[1];
        part gridRelay  : GridRelay[1];
        part power      : PowerModule[1];
        part backplane  : Backplane[1];
        part manager    : SystemManager[1];
        part meter      : IntegratedMeter[1];

        part c01 : CircuitModule[1];
        part c02 : CircuitModule[1];

        part enclosure : Enclosure[1];

        // External interface bindings
        bind phaseIn = mainsTerminals.phaseIn;
        bind neutralIn = mainsTerminals.neutralIn;
        bind earthIn = mainsTerminals.earthIn;

        bind t1sExpansion = backplane.t1sSpare;

        bind derA = manager.derA;
        bind derB = manager.derB;

        // Load outputs: connect phase and neutral from circuits to external AC1PPort
        interface connect (c01.phaseOut, load01);
        interface connect (c01.neutralOut, load01);
        interface connect (c02.phaseOut, load02);
        interface connect (c02.neutralOut, load02);

        // Power path: Mains terminals -> MainSwitch -> SPD -> Meter -> GridRelay -> Supply busbars -> Circuit modules
        
        // 1. Mains terminals: pass-through for phase, neutral, earth
        interface connect (mainsTerminals.phaseIn, mainsTerminals.phaseOut);
        interface connect (mainsTerminals.neutralIn, mainsTerminals.neutralOut);
        interface connect (mainsTerminals.earthIn, mainsTerminals.earthOut);
        interface connect (mainsTerminals.earthOut, earthBusbar.earth);
        
        // 2. Mains terminals -> MainSwitch (phase and neutral)
        interface connect (mainsTerminals.phaseOut, mainSwitch.phaseIn);
        interface connect (mainsTerminals.neutralOut, mainSwitch.neutralIn);
        
        // 3. MainSwitch -> SPD -> Meter (phase in/out, neutral shunt)
        // SPD shunts L->E and N->E separately via GDT/N-E combined cartridge
        interface connect (mainSwitch.phaseOut, spd.phaseIn);
        interface connect (mainSwitch.neutralOut, spd.neutralIn);
        interface connect (spd.phaseOut, meter.phaseIn);
        interface connect (spd.neutralOut, meter.neutralIn);
        interface connect (spd.earth, earthBusbar.earth);  // SPD shunts to earth
        interface connect (meter.phaseOut, gridRelay.phaseIn);
        interface connect (meter.neutralIn, gridRelay.neutralIn);  // Neutral shunt through meter (pass-through, no physical terminal)
        
        // 4. Meter -> GridRelay (phase only, neutral passes through)
        // Neutral already connected from meter to grid relay
        
        // 5. GridRelay -> Supply busbars (phase and neutral)
        interface connect (gridRelay.phaseOut, busbars.phaseIn);
        interface connect (gridRelay.neutralOut, busbars.neutralIn);

        // Power module taps from busbars + earth; provides 24V into backplane
        interface connect (busbars.phaseOut, power.phaseIn);
        interface connect (busbars.neutralOut, power.neutralIn);
        interface connect (earthBusbar.earth, power.earth);
        interface connect (power.dc24Out, backplane.dc24In);

        // Comms / backplane distribution (10BASE-T1S)
        interface connect (backplane.t1sBus, manager.t1s);
        interface connect (backplane.t1sBus, meter.t1s);
        interface connect (backplane.t1sBus, power.t1s);

        interface connect (backplane.t1sBus, c01.t1s);
        interface connect (backplane.t1sBus, c02.t1s);

        // SPI (UI bus)
        interface connect (backplane.spi, mainSwitch.uiSpi);

        // 6. Supply busbars -> Circuit modules
        interface connect (busbars.phaseOut, c01.phaseIn);
        interface connect (busbars.phaseOut, c02.phaseIn);
        interface connect (busbars.neutralOut, c01.neutralIn);
        interface connect (busbars.neutralOut, c02.neutralIn);

        // Earth distribution to all modules via earth busbar
        interface connect (earthBusbar.earth, manager.earth);
        interface connect (earthBusbar.earth, meter.earth);
        interface connect (earthBusbar.earth, mainSwitch.earth);
        interface connect (earthBusbar.earth, gridRelay.earth);
        interface connect (earthBusbar.earth, c01.earth);
        interface connect (earthBusbar.earth, c02.earth);

        // Controls + status (circuit modules communicate via T1S bus)
        interface connect (manager.ctrlMainSwitch, mainSwitch.ctrl);
        interface connect (manager.ctrlGridRelay,  gridRelay.ctrl);

        interface connect (spd.status, manager.stsSpd);
        interface connect (gridRelay.status, manager.stsRelay);
    }

    // Concrete system instance
    part panel : Gen2Panel[1];
}
