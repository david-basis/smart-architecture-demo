# OnShape Utilities

Utility scripts for working with OnShape documents, parts, and clearance verification.

## validate_meter_clearance.py

Demonstrates the complete clearance validation flow from SysML requirements through part definitions to OnShape physical verification.

### Usage

```bash
cd utilities
python validate_meter_clearance.py
```

### What it does

1. Loads part mapping from `onshape_part_mapping.json`
2. Calculates required clearance from voltage/current using IEC 61010-1 and IEC 61439-1
3. Queries OnShape for actual surface-to-surface distances using FeatureScript
4. Compares actual vs required clearances
5. Generates compliance report with pass/fail status

### Output

The script prints:
- Validation flow overview
- Mapping file summary
- Detailed results for each clearance pair:
  - Terminal names and materials
  - Voltage and current ratings
  - Required clearance (worst case from IEC standards)
  - Actual distance from OnShape
  - Margin (actual - required)
  - Pass/fail status

## find_conductive_parts.py

Searches for parts with conductive material parameters in an OnShape document.

### Usage

```bash
cd utilities
python find_conductive_parts.py <document_id> [workspace_id] [element_id]
```

### Example

```bash
python find_conductive_parts.py 394aa47131b35eec8c9ea996
```

### What it does

1. Connects to OnShape using credentials from `.env` file
2. Fetches all Part Studios from the specified document (or specific element)
3. Gets all parts from each Part Studio
4. Checks each part's material property (tries multiple API endpoints)
5. Identifies parts with conductive materials (copper, aluminum, steel, etc.)
6. Prints a summary of all conductive parts found

### Output

The script prints:
- Part name
- Material
- Part ID
- Element (Part Studio) name and ID
- Summary of all conductive parts

### Conductive Materials Detected

The script recognizes common conductive materials including:
- Copper, Brass, Bronze
- Aluminum, Steel, Stainless Steel
- Silver, Gold, Tin, Lead, Zinc, Nickel
- Any material containing "conductive", "metal", or "metallic"

## analyze_conductor_distances.py

Analyzes distances between conductive parts in an OnShape document, useful for identifying clearance issues.

### Usage

```bash
cd utilities
python analyze_conductor_distances.py <document_id> [workspace_id] [element_id] [--material-filter <keyword>]
```

### Example

```bash
python analyze_conductor_distances.py 394aa47131b35eec8c9ea996 --material-filter "Steel Class 8.8"
```

### What it does

1. Finds all conductive parts in the document (optionally filtered by material)
2. Calculates minimum distances between all pairs using OnShape FeatureScript
3. Sorts pairs by distance (closest first)
4. Reports potential clearance issues

### Output

The script prints:
- List of conductive parts found
- Distance matrix for all pairs
- Sorted list of closest pairs
- Warnings for pairs that may need clearance verification

## list_documents.py

Lists all OnShape documents accessible by the API key.

### Usage

```bash
cd utilities
python list_documents.py
```

### What it does

1. Authenticates with OnShape API
2. Lists all accessible documents
3. Shows document name, ID, and creation date

## test_auth.py

Tests OnShape API authentication.

### Usage

```bash
cd utilities
python test_auth.py
```

### What it does

1. Loads credentials from `.env` file
2. Tests authentication with OnShape API
3. Reports success or failure

## test_document_access.py

Tests access to a specific OnShape document.

### Usage

```bash
cd utilities
python test_document_access.py <document_id>
```

### Example

```bash
python test_document_access.py 394aa47131b35eec8c9ea996
```

### What it does

1. Tests access to the specified document
2. Lists available workspaces
3. Reports permissions status

## test_clearance_verification.py

Tests the clearance verification MCP tool directly.

### Usage

```bash
cd utilities
python test_clearance_verification.py
```

### What it does

1. Initializes the OnShape client
2. Calls the clearance verification tool
3. Prints results

## Common Requirements

All utilities require:
- OnShape API credentials in `.env` file or environment variables:
  - `ONSHAPE_ACCESS_KEY`
  - `ONSHAPE_SECRET_KEY`
- Python dependencies from `../requirements.txt`

## Notes

- **Rate Limiting**: OnShape API has rate limits. The clearance verification tool includes delays between requests to avoid 429 errors.
- **FeatureScript Distance**: Accurate distance calculations use OnShape's FeatureScript `evDistance` function, which matches the native measure tool.
- **Material Detection**: Material properties may not be available for all parts, especially STEP-imported documents. The utilities try multiple API endpoints to find material information.
