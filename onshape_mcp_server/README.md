# OnShape MCP Server

Model Context Protocol (MCP) server for bridging SysML models with OnShape 3D CAD models, enabling model-based verification and validation (MBSE/V&V) for electrical clearance requirements.

## Overview

This server provides a bridge between:
- **SysML Models** (`Gen2Panel1P12.sysml`) - System architecture, requirements, and part definitions
- **OnShape 3D CAD** - Physical geometry and material properties
- **IEC Standards** - Electrical clearance requirements (IEC 61010-1, IEC 61439-1)

It enables automated verification that physical parts in OnShape meet electrical clearance requirements defined in SysML, using industry standards for calculation.

## Purpose

This project demonstrates **Model-Based Systems Engineering (MBSE)** and **Model-Based Verification & Validation** by:

1. **Requirements Traceability**: SysML requirements (`ElectricalClearanceReq`) are linked to physical parts
2. **Automated Verification**: Physical distances in OnShape are automatically compared to calculated requirements
3. **Standards Compliance**: IEC clearance standards are encoded and automatically applied
4. **Single Source of Truth**: SysML model remains the authoritative source, with OnShape providing physical validation

## Project Context

This server is part of a larger MBSE demonstration for the **Gen2Panel** electrical distribution system:

- **SysML Model**: `Gen2Panel1P12.sysml` defines the system architecture, including:
  - `IntegratedMeter` with `MeterTerminal` parts
  - `ElectricalClearanceReq` requirement (REQ-ELECTRICAL-CLEARANCE-001)
  - Part definitions that satisfy requirements
  
- **OnShape CAD**: Physical 3D models of meter terminals and screws
- **This Server**: Bridges the gap between logical (SysML) and physical (OnShape) models

## Features

- **Clearance Verification**: Verify electrical clearance requirements using IEC 61010-1 and IEC 61439-1 standards
- **Distance Calculation**: Accurate surface-to-surface distance measurement using OnShape FeatureScript (`evDistance`)
- **Material Sync**: Dynamically fetch material properties from OnShape API
- **Part Mapping**: Link SysML part definitions to OnShape part IDs via JSON mapping file
- **Terminal Tools**: Query terminal information, verify existence, and analyze clearances
- **Rate Limiting**: Built-in delays to handle OnShape API rate limits

## Prerequisites

- Python 3.8+
- OnShape account with API access
- OnShape API credentials (access key and secret key)
- Access to the OnShape document containing the physical parts

## Setup

### 1. Install Dependencies

```bash
cd onshape_mcp_server
pip install -r requirements.txt
```

**Dependencies:**
- `mcp>=1.0.0` - Model Context Protocol server framework
- `httpx>=0.27.0` - Async HTTP client for OnShape API
- `numpy>=1.24.0` - Numerical computations (for mesh distance calculations)

### 2. Configure OnShape Credentials

Create a `.env` file in the `onshape_mcp_server` directory:

```bash
ONSHAPE_ACCESS_KEY=your_access_key_here
ONSHAPE_SECRET_KEY=your_secret_key_here
```

**Getting OnShape API Keys:**
1. Log into OnShape
2. Go to Account Settings → Applications → Create Application
3. Copy the Access Key and Secret Key
4. Ensure the API key has access to the documents you want to analyze

**Alternative:** Export as environment variables:
```bash
export ONSHAPE_ACCESS_KEY=your_access_key
export ONSHAPE_SECRET_KEY=your_secret_key
```

### 3. Configure Part Mapping

Edit `onshape_part_mapping.json` to link your SysML parts to OnShape part IDs:

```json
{
  "document_id": "your_document_id",
  "workspace_id": "your_workspace_id",
  "element_id": "your_element_id",
  "part_mappings": {
    "meter.phaseInTerminal": {
      "onshape_part_id": "KFDD",
      "voltage": 230.0,
      "current": 80.0,
      "description": "Phase input terminal"
    }
  },
  "clearance_pairs": [
    {
      "terminal1": "meter.phaseInTerminal",
      "terminal2": "meter.phaseOutTerminal",
      "description": "Phase in to phase out clearance"
    }
  ]
}
```

**Finding OnShape IDs:**
- Document ID: From the OnShape URL: `https://cad.onshape.com/documents/{document_id}/...`
- Workspace ID: From the URL: `.../w/{workspace_id}/...`
- Element ID: From the URL: `.../e/{element_id}/...`
- Part ID: Use the `utilities/find_conductive_parts.py` script or OnShape API

### 4. Run the Server

```bash
python -m onshape_mcp.server
```

The server will start and be ready to accept MCP tool calls.

## MCP Tools

### `verify_clearance_requirements`

**Primary tool for clearance verification.** Verifies electrical clearance requirements for terminal pairs using IEC standards.

**Parameters:**
- `mapping_file` (string, optional): Path to part mapping JSON file (default: `onshape_part_mapping.json`)

**Returns:**
- Compliance report with required vs actual clearances
- Material information (synced dynamically from OnShape)
- Clearance calculations per IEC 61010-1 and IEC 61439-1
- Pass/fail status for each clearance pair
- Margin calculations (actual - required)

**Example Usage:**
```python
# Via MCP client
result = await client.call_tool("verify_clearance_requirements", {
    "mapping_file": "onshape_part_mapping.json"
})
```

### `get_terminal_info`

Get information about an OnShape terminal/part by ID.

**Parameters:**
- `document_id`: OnShape document ID
- `workspace_id`: Workspace ID
- `element_id`: Element (Part Studio) ID
- `part_id`: Part ID for the terminal

### `verify_terminal_exists`

Verify that a terminal/part exists in OnShape.

**Parameters:**
- `document_id`: OnShape document ID
- `workspace_id`: Workspace ID
- `element_id`: Element (Part Studio) ID
- `part_id`: Part ID for the terminal

### `get_terminal_bounding_box`

Get bounding box of a terminal for clearance analysis.

**Parameters:**
- `document_id`: OnShape document ID
- `workspace_id`: Workspace ID
- `element_id`: Element (Part Studio) ID
- `part_id`: Part ID for the terminal

### `analyze_terminal_clearances`

Analyze clearances between multiple terminals.

**Parameters:**
- `document_id`: OnShape document ID
- `workspace_id`: Workspace ID
- `element_id`: Element (Part Studio) ID
- `terminals`: Array of terminal objects with `part_id` and optional `name`
- `required_clearance`: Required clearance in meters (default: 0.0)

## Workflow: Requirements → Parts → OnShape

This server implements a complete model-based V&V workflow:

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

`onshape_part_mapping.json` links SysML part names to OnShape part IDs and defines clearance pairs to verify.

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

## IEC Clearance Standards

The server implements clearance lookup tables for:

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

## Architecture

```
onshape_mcp_server/
├── onshape_mcp/
│   ├── api/
│   │   ├── client.py              # HTTP client with OnShape authentication
│   │   ├── parts.py               # Parts API with FeatureScript distance calculation
│   │   ├── clearance.py           # Clearance analysis utilities
│   │   └── iec_clearance.py       # IEC 61010-1 and IEC 61439-1 lookup tables
│   ├── tools/
│   │   ├── __init__.py            # Tool exports
│   │   ├── terminal_tools.py      # Terminal query tools
│   │   └── clearance_verification.py  # Main clearance verification tool
│   └── server.py                  # Main MCP server entry point
├── utilities/                     # Standalone utility scripts
│   ├── validate_meter_clearance.py    # Complete validation exercise
│   ├── find_conductive_parts.py        # Find conductive parts in document
│   ├── analyze_conductor_distances.py  # Analyze distances between conductors
│   ├── list_documents.py               # List accessible OnShape documents
│   ├── test_auth.py                    # Test API authentication
│   ├── test_document_access.py         # Test document access
│   └── README.md                       # Utility documentation
├── onshape_part_mapping.json      # SysML to OnShape part mapping
├── requirements.txt               # Python dependencies
└── README.md                       # This file
```

## Key Components

### API Layer (`onshape_mcp/api/`)

- **`client.py`**: Handles OnShape API authentication and HTTP requests
- **`parts.py`**: Parts API with FeatureScript integration for accurate distance measurement
- **`clearance.py`**: Clearance analysis utilities
- **`iec_clearance.py`**: IEC standard lookup tables and calculation logic

### Tools Layer (`onshape_mcp/tools/`)

- **`clearance_verification.py`**: Main tool for clearance requirement verification
- **`terminal_tools.py`**: Terminal query and analysis tools

### Utilities (`utilities/`)

Standalone scripts for development, testing, and demonstration. See `utilities/README.md` for details.

## Distance Calculation

The server uses OnShape's FeatureScript `evDistance` function for accurate surface-to-surface distance measurement. This:

- Matches OnShape's native measure tool accuracy
- Works with complex 3D geometries
- Handles STEP-imported parts
- Provides millimeter-precision results

**Implementation:**
1. Retrieves all parts from the Part Studio
2. Finds part indices for the specified part IDs
3. Executes FeatureScript with `evDistance` function
4. Returns distance in meters (converted to mm for reporting)

## Material Detection

Material properties are dynamically synced from OnShape:

1. Tries primary part metadata endpoint
2. Falls back to metadata endpoint if needed
3. Handles different OnShape API response formats
4. Returns "Unknown" if material cannot be determined

**Note:** STEP-imported parts may not have material properties in OnShape. The system handles this gracefully.

## Rate Limiting

OnShape API has rate limits. The server includes:

- 1.5 second delay between clearance verification requests
- Error handling for 429 (Too Many Requests) responses
- Clear error messages when rate limits are hit

If you encounter rate limiting:
- Wait a few minutes before retrying
- Reduce the number of clearance pairs in a single run
- Consider increasing the delay in `clearance_verification.py`

## Usage Examples

### Standalone Validation Script

```bash
cd utilities
python validate_meter_clearance.py
```

This runs a complete validation exercise demonstrating the Requirements → Parts → OnShape flow.

### Via MCP Server

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

## Integration with SysML Model

The SysML model (`Gen2Panel1P12.sysml`) defines:

- **Requirements**: `ElectricalClearanceReq` with ID and text
- **Parts**: `MeterTerminal` parts that satisfy the requirement
- **Allocations**: Comments documenting logical-to-physical port allocation

The mapping file (`onshape_part_mapping.json`) provides the bridge:
- Links SysML part names (e.g., `meter.phaseInTerminal`) to OnShape part IDs
- Defines electrical properties (voltage, current) for each part
- Specifies clearance pairs to verify

This separation keeps the SysML model clean while enabling physical verification.

## Development

### Adding New Clearance Standards

Edit `onshape_mcp/api/iec_clearance.py`:
1. Add lookup table dictionary
2. Add lookup function
3. Update `calculate_clearance()` to include new standard
4. Worst-case selection is automatic

### Adding New Tools

1. Create tool definition in `onshape_mcp/tools/`
2. Export in `onshape_mcp/tools/__init__.py`
3. Register handler in `onshape_mcp/server.py`

### Testing

Use the utility scripts in `utilities/` for testing:
- `test_auth.py` - Test authentication
- `test_document_access.py` - Test document access
- `validate_meter_clearance.py` - Full validation exercise

## Troubleshooting

### 429 Too Many Requests

- Wait a few minutes before retrying
- Check if you're making too many requests in quick succession
- Increase delay in `clearance_verification.py`

### Material Not Found

- STEP-imported parts may not have materials
- Check OnShape document to verify material assignment
- System will return "Unknown" and continue

### Distance Calculation Returns 0.0

- Verify part IDs are correct in mapping file
- Check that parts exist in the specified element
- Ensure parts are not overlapping (0.0 may be accurate)

### Authentication Errors

- Verify `.env` file has correct credentials
- Check that API key has access to the document
- Use `utilities/test_auth.py` to verify credentials

## Future Enhancements

Potential areas for extension:

- **Auto Mode**: Automatically detect conductive parts and generate clearance pairs
- **More Standards**: Add additional IEC standards (e.g., IEC 60664-1)
- **Creepage Distance**: Add creepage distance calculation in addition to clearance
- **3D Visualization**: Generate visualizations of clearance violations
- **Batch Processing**: Process multiple documents/elements in one run
- **SysML Integration**: Direct integration with SysML modeling tools

## Contributing

When contributing:

1. Follow the existing code structure
2. Add tests using utility scripts
3. Update this README with new features
4. Document any new IEC standards or lookup tables
5. Handle rate limiting and errors gracefully

## License

MIT License

## Related Files

- **SysML Model**: `../Gen2Panel1P12.sysml` - System architecture and requirements
- **Utilities**: `utilities/README.md` - Standalone utility scripts documentation
- **Mapping File**: `onshape_part_mapping.json` - SysML to OnShape part mapping

## References

- **IEC 61010-1**: Safety requirements for electrical equipment for measurement, control, and laboratory use
- **IEC 61439-1**: Low-voltage switchgear and controlgear assemblies
- **OnShape API**: https://dev-portal.onshape.com/
- **Model Context Protocol**: https://modelcontextprotocol.io/
