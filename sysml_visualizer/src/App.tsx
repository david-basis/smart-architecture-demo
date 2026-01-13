import { useState, useCallback } from 'react';
import { ReactFlowProvider, ReactFlowInstance } from '@xyflow/react';
import { ModelProvider, useModel } from './model/ModelContext';
import { Explorer } from './components/Explorer';
import { ElementDetails } from './components/ElementDetails';
import { Toolbar } from './components/Toolbar';
import { DiagramCanvas } from './components/DiagramCanvas';

// Demo SysML model - Gen2Panel excerpt
const DEMO_MODEL = `package Gen2Panel1P12 {
    item def ACPhase;
    item def ACNeutral;
    item def ACEarth;
    item def DC24V;
    item def T1SFrame;

    port def AC1PPort {
        inout item phase : ACPhase;
        inout item neutral : ACNeutral;
        inout item earth : ACEarth;
    }

    port def PhasePort {
        inout item phase : ACPhase;
    }

    port def NeutralPort {
        inout item neutral : ACNeutral;
    }

    port def EarthPort {
        inout item earth : ACEarth;
    }

    port def DC24Port {
        inout item dc24 : DC24V;
    }

    port def T1SPort {
        inout item t1sframe : T1SFrame;
    }

    part def MeterTerminal;
    part def ShuntBreaker;
    part def RCDSensor;
    part def RelayCircuit;

    requirement def ElectricalClearanceReq {
        id = "REQ-ELECTRICAL-CLEARANCE-001";
        text = "Electrical parts shall meet minimum clearance requirements based on voltage and current ratings per IEC 61010-1 and IEC 61439-1 standards.";
    }

    part def MainsTerminals {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
        port earthIn : EarthPort;
        port earthOut : EarthPort;
    }

    part def SupplyBusbars {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
    }

    part def EarthBusbar {
        port earth : EarthPort;
    }

    part def SurgeProtectionDevice {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
        port earth : EarthPort;
    }

    part def PowerModule {
        port phaseIn : PhasePort;
        port neutralIn : NeutralPort;
        port earth : EarthPort;
        port dc24Out : DC24Port;
        port t1s : T1SPort;
    }

    part def Backplane {
        port dc24In : DC24Port;
        port t1sBus : T1SPort;
        port t1sSpare : T1SPort;
    }

    part def IntegratedMeter {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port earth : EarthPort;
        port t1s : T1SPort;

        part phaseInTerminal : MeterTerminal[1];
        part phaseOutTerminal : MeterTerminal[1];
        part neutralInTerminal : MeterTerminal[1];
    }

    part def SystemManager {
        port t1s : T1SPort;
        port earth : EarthPort;
    }

    part def ConfigurableMainSwitch {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
        port earth : EarthPort;
    }

    part def GridRelay {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
        port earth : EarthPort;

        part phasePole : RelayCircuit[1];
        part neutralPole : RelayCircuit[1];
        part shuntBreaker : ShuntBreaker[1];

        state def GridRelayStateMachine {
            entry; then OPEN;

            state OPEN {
                entry action enterOpenState {}
            }

            state CLOSING {
                entry action enterClosingState {}
            }

            state CLOSED {
                entry action enterClosedState {}
            }

            state OPENING {
                entry action enterOpeningState {}
            }

            state FAULT {
                entry action enterFaultState {}
            }

            transition t1 first OPEN accept close_cmd then CLOSING;
            transition t2 first CLOSING accept success then CLOSED;
            transition t3 first CLOSING accept failure then OPEN;
            transition t4 first CLOSED accept open_cmd then OPENING;
            transition t5 first OPENING accept success then OPEN;
        }
    }

    part def CircuitModule {
        port phaseIn : PhasePort;
        port phaseOut : PhasePort;
        port neutralIn : NeutralPort;
        port neutralOut : NeutralPort;
        port earth : EarthPort;
        port t1s : T1SPort;

        part shuntBreaker : ShuntBreaker[1];
        part rcdSensor : RCDSensor[1];
        part relayCircuit : RelayCircuit[1];
    }

    part def Gen2Panel {
        port phaseIn : PhasePort;
        port neutralIn : NeutralPort;
        port earthIn : EarthPort;
        port load01 : AC1PPort;
        port load02 : AC1PPort;

        part mainsTerminals : MainsTerminals[1];
        part busbars : SupplyBusbars[1];
        part earthBusbar : EarthBusbar[1];
        part spd : SurgeProtectionDevice[1];
        part mainSwitch : ConfigurableMainSwitch[1];
        part gridRelay : GridRelay[1];
        part power : PowerModule[1];
        part backplane : Backplane[1];
        part manager : SystemManager[1];
        part meter : IntegratedMeter[1];
        part c01 : CircuitModule[1];
        part c02 : CircuitModule[1];

        interface connect (mainsTerminals.phaseOut, mainSwitch.phaseIn);
        interface connect (mainSwitch.phaseOut, spd.phaseIn);
        interface connect (spd.phaseOut, meter.phaseIn);
        interface connect (meter.phaseOut, gridRelay.phaseIn);
        interface connect (gridRelay.phaseOut, busbars.phaseIn);
    }

    part panel : Gen2Panel[1];
}`;

function AppContent() {
  const { loadModel } = useModel();
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance | null>(null);

  const handleLoadDemo = useCallback(() => {
    loadModel(DEMO_MODEL);
  }, [loadModel]);

  const handleFileSelect = useCallback(async (file: File) => {
    const text = await file.text();
    loadModel(text);
  }, [loadModel]);

  const handleZoomIn = useCallback(() => {
    flowInstance?.zoomIn();
  }, [flowInstance]);

  const handleZoomOut = useCallback(() => {
    flowInstance?.zoomOut();
  }, [flowInstance]);

  const handleFitView = useCallback(() => {
    flowInstance?.fitView({ padding: 0.2 });
  }, [flowInstance]);

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <Toolbar
        onLoadDemo={handleLoadDemo}
        onFileSelect={handleFileSelect}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFitView={handleFitView}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Explorer */}
        <div className="w-64 bg-white border-r flex flex-col">
          <Explorer />
        </div>

        {/* Main diagram area */}
        <DiagramCanvas
          flowInstance={flowInstance}
          setFlowInstance={setFlowInstance}
        />

        {/* Right sidebar - Details */}
        <div className="w-72 bg-white border-l flex flex-col">
          <ElementDetails />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ReactFlowProvider>
      <ModelProvider>
        <AppContent />
      </ModelProvider>
    </ReactFlowProvider>
  );
}

export default App;
