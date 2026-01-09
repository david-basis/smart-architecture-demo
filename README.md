# Smart Architecture Demo

Model-Based Systems Engineering (MBSE) demonstration project bridging SysML models with OnShape 3D CAD for automated verification and validation of electrical clearance requirements.

## Overview

This repository demonstrates **Model-Based Verification & Validation (MBSE/V&V)** by connecting:

- **SysML Models** (`Gen2Panel1P12.sysml`) - System architecture, requirements, and part definitions
- **OnShape 3D CAD** - Physical geometry and material properties via API
- **IEC Standards** - Electrical clearance requirements (IEC 61010-1, IEC 61439-1)
- **MCP Server** - Model Context Protocol server for automated verification

The project enables automated verification that physical parts in OnShape meet electrical clearance requirements defined in SysML, using industry standards for calculation.

## Project Structure

```
smart-architecture-demo/
├── Gen2Panel1P12.sysml              # SysML system model with requirements and parts
├── RCD_Requirements_ANZ.md          # Requirements documentation
├── onshape_mcp_server/               # OnShape MCP server implementation
│   ├── onshape_mcp/                 # MCP server package
│   │   ├── api/                     # OnShape API client and utilities
│   │   ├── tools/                   # MCP tools for clearance verification
│   │   └── server.py                # MCP server entry point
│   ├── utilities/                   # Standalone utility scripts
│   ├── onshape_part_mapping.json    # SysML to OnShape part mapping
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # MCP server documentation
└── README.md                         # This file
```

## Purpose

This project demonstrates **Model-Based Systems Engineering (MBSE)** and **Model-Based Verification & Validation** by:

1. **Requirements Traceability**: SysML requirements (`ElectricalClearanceReq`) are linked to physical parts
2. **Automated Verification**: Physical distances in OnShape are automatically compared to calculated requirements
3. **Standards Compliance**: IEC clearance standards are encoded and automatically applied
4. **Single Source of Truth**: SysML model remains the authoritative source, with OnShape providing physical validation

## Gen2Panel System

The **Gen2Panel** is an electrical distribution system with the following components:

- **Mains Terminals** - Phase, neutral, and earth input terminals
- **Configurable Main Switch** - Main circuit breaker with RCD protection
- **Surge Protection Device (SPD)** - Lightning protection
- **Integrated Meter** - Energy metering with T1S communication
- **Grid Relay** - Grid connection control
- **Circuit Modules** - Distribution circuits

The SysML model (`Gen2Panel1P12.sysml`) defines:
- System architecture and component connections
- Port definitions for electrical interfaces
- Requirements including `ElectricalClearanceReq` (REQ-ELECTRICAL-CLEARANCE-001)
- Part definitions that satisfy requirements (e.g., `MeterTerminal` parts)

## OnShape MCP Server

The MCP server (`onshape_mcp_server/`) provides:

- **Clearance Verification**: Verify electrical clearance requirements using IEC 61010-1 and IEC 61439-1 standards
- **Distance Calculation**: Accurate surface-to-surface distance measurement using OnShape FeatureScript (`evDistance`)
- **Material Sync**: Dynamically fetch material properties from OnShape API
- **Part Mapping**: Link SysML part definitions to OnShape part IDs via JSON mapping file

See [`onshape_mcp_server/README.md`](onshape_mcp_server/README.md) for detailed setup and usage instructions.

## Workflow: Requirements → Parts → OnShape

This project implements a complete model-based V&V workflow:

### 1. Requirements Definition (SysML)

```sysml
requirement def ElectricalClearanceReq {
    id = "REQ-ELECTRICAL-CLEARANCE-001";
    text = "Electrical parts shall meet minimum clearance requirements 
           based on voltage and current ratings per IEC 61010-1 and IEC 61439-1 
           standards. Worst case (maximum) clearance is selected from both standards.";
}
```

### 2. Part Definition (SysML)

```sysml
part def MeterTerminal {
    // Satisfies: ElectricalClearanceReq
    // Attributes managed via onshape_part_mapping.json:
    // - voltage: Real (default 230.0 V)
    // - current: Real (default 80.0 A)
    // - material: String (synced from OnShape dynamically)
    // - minClearance: Real (calculated from voltage/current per IEC standards)
}

part def IntegratedMeter {
    part phaseInTerminal  : MeterTerminal[1];
    part phaseOutTerminal : MeterTerminal[1];
    part neutralInTerminal : MeterTerminal[1];
    // ... allocation comments link logical ports to physical terminals
}
```

### 3. Part Mapping (JSON)

`onshape_mcp_server/onshape_part_mapping.json` links SysML part names to OnShape part IDs and defines clearance pairs to verify.

### 4. Verification (MCP Tool)

The `verify_clearance_requirements` tool:
1. Loads the mapping file
2. Calculates required clearance from voltage/current using IEC standards
3. Queries OnShape for actual surface-to-surface distances (FeatureScript)
4. Compares actual vs required
5. Reports compliance status

### 5. Results

The tool returns a JSON report with:
- Required clearance (worst case from IEC 61010-1 and IEC 61439-1)
- Actual distance from OnShape
- Pass/fail status
- Material information
- Clearance margin

## Quick Start

### Prerequisites

- Python 3.8+
- OnShape account with API access
- OnShape API credentials (access key and secret key)

### Setup

1. **Install Dependencies**

```bash
cd onshape_mcp_server
pip install -r requirements.txt
```

2. **Configure OnShape Credentials**

Create `onshape_mcp_server/.env`:

```bash
ONSHAPE_ACCESS_KEY=your_access_key_here
ONSHAPE_SECRET_KEY=your_secret_key_here
```

3. **Configure Part Mapping**

Edit `onshape_mcp_server/onshape_part_mapping.json` to link your SysML parts to OnShape part IDs.

4. **Run Validation**

```bash
cd onshape_mcp_server/utilities
python validate_meter_clearance.py
```

## IEC Clearance Standards

The project implements clearance lookup tables for:

- **IEC 61010-1** (Measurement Equipment): 
  - Supports functional, basic, and reinforced insulation types
  - Voltage range: 50V to 1000V
  - Clearance values: 0.5mm to 25mm depending on voltage and insulation type

- **IEC 61439-1** (Low-voltage Switchgear): 
  - General clearance requirements for switchgear assemblies
  - Voltage range: 50V to 1000V
  - Clearance values: 1.5mm to 12mm depending on voltage

**Calculation Logic:**
- Both standards are applied to each clearance pair
- The worst-case (maximum) clearance requirement is selected
- This ensures compliance with both standards

## Key Features

- **Model-Based**: SysML model as single source of truth
- **Automated Verification**: Physical validation via OnShape API
- **Standards Compliance**: IEC clearance standards built-in
- **Accurate Measurements**: FeatureScript-based distance calculation
- **Dynamic Material Sync**: Material properties from OnShape
- **Rate Limiting**: Built-in handling for API rate limits

## Documentation

- **[OnShape MCP Server](onshape_mcp_server/README.md)** - Detailed MCP server documentation
- **[Utilities](onshape_mcp_server/utilities/README.md)** - Utility scripts documentation
- **[SysML Model](Gen2Panel1P12.sysml)** - System architecture and requirements
- **[Requirements](RCD_Requirements_ANZ.md)** - Requirements documentation

## Usage Examples

### Standalone Validation

```bash
cd onshape_mcp_server/utilities
python validate_meter_clearance.py
```

### MCP Server

```bash
cd onshape_mcp_server
python -m onshape_mcp.server
```

### Via Python API

```python
from onshape_mcp.api.client import OnShapeClient
from onshape_mcp.tools.clearance_verification import (
    initialize_verification_tools,
    handle_verify_clearance_requirements
)

# Initialize
client = OnShapeClient()
initialize_verification_tools(client)

# Run verification
result = await handle_verify_clearance_requirements({
    "mapping_file": "onshape_part_mapping.json"
})
```

## Development

### Adding New Clearance Standards

Edit `onshape_mcp_server/onshape_mcp/api/iec_clearance.py`:
1. Add lookup table dictionary
2. Add lookup function
3. Update `calculate_clearance()` to include new standard
4. Worst-case selection is automatic

### Testing

Use the utility scripts in `onshape_mcp_server/utilities/`:
- `test_auth.py` - Test authentication
- `test_document_access.py` - Test document access
- `validate_meter_clearance.py` - Full validation exercise

## Troubleshooting

### Rate Limiting (429 Errors)

- Wait 10-15 minutes for rate limit window to reset
- Reduce number of clearance pairs per run
- Increase delay between requests

### Authentication Errors

- Verify `.env` file has correct credentials
- Check that API key has access to the document
- Use `utilities/test_auth.py` to verify credentials

### Distance Calculation Issues

- Verify part IDs are correct in mapping file
- Check that parts exist in the specified element
- Ensure parts are not overlapping (0.0 may be accurate)

## Future Enhancements

- **Auto Mode**: Automatically detect conductive parts and generate clearance pairs
- **More Standards**: Add additional IEC standards (e.g., IEC 60664-1)
- **Creepage Distance**: Add creepage distance calculation in addition to clearance
- **3D Visualization**: Generate visualizations of clearance violations
- **Batch Processing**: Process multiple documents/elements in one run
- **SysML Integration**: Direct integration with SysML modeling tools

## License

MIT License

## References

- **IEC 61010-1**: Safety requirements for electrical equipment for measurement, control, and laboratory use
- **IEC 61439-1**: Low-voltage switchgear and controlgear assemblies
- **OnShape API**: https://dev-portal.onshape.com/
- **Model Context Protocol**: https://modelcontextprotocol.io/
