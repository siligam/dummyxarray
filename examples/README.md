# Examples

This directory contains example scripts demonstrating various features of dummyxarray.

## Running Examples

All examples can be run using pixi:

```bash
# Run the main example (comprehensive overview)
pixi run example

# Or run individual examples directly
pixi run python examples/example.py
pixi run python examples/example_from_xarray.py
pixi run python examples/example_populate.py
pixi run python examples/example_history.py
```

## Example Files

### `example.py`

Comprehensive example covering all major features:
- Creating datasets with dimensions, coordinates, and variables
- Setting metadata and encoding
- Validation
- Converting to xarray.Dataset
- Writing to Zarr format
- Saving/loading YAML specifications

**Run:** `pixi run example`

### `example_from_xarray.py`

Demonstrates extracting metadata from existing xarray datasets:
- Creating DummyDataset from xarray.Dataset
- Preserving metadata without data
- Using templates for multiple datasets
- Encoding preservation

**Run:** `pixi run python examples/example_from_xarray.py`

### `example_populate.py`

Shows how to populate datasets with random but meaningful data:
- Automatic data generation based on variable metadata
- Climate variable patterns (temperature, precipitation, etc.)
- Reproducible random data with seeds
- Template-based workflows

**Run:** `pixi run python examples/example_populate.py`

### `example_history.py`

Demonstrates operation history tracking for reproducible workflows:
- Recording all operations automatically
- Exporting history as JSON, YAML, or Python code
- Replaying history to recreate datasets
- Saving dataset recipes for sharing

**Run:** `pixi run python examples/example_history.py`

## Output Files

Examples may generate output files in this directory:
- `*.zarr/` - Zarr datasets
- `*.nc` - NetCDF files
- `*.yaml` - YAML specifications
- `*.json` - JSON specifications

These files are gitignored and safe to delete.

## Interactive Usage

You can also use these examples interactively:

```bash
# Start IPython with proper PYTHONPATH
pixi run ipython

# Then import and explore
from dummyxarray import DummyDataset
ds = DummyDataset()
# ... experiment interactively
```

## More Information

See the main [README.md](../README.md) for complete documentation and API reference.
