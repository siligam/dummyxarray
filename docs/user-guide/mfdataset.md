# Multi-file Dataset Support

The `open_mfdataset()` feature allows you to work with multiple NetCDF files as a single dataset, tracking which files contain specific coordinate ranges. This is particularly useful for large climate datasets split across multiple files.

## Overview

Unlike xarray's `open_mfdataset()` which loads data into memory, DummyDataset's version only reads **metadata** from files. This makes it ideal for:

- Planning data access patterns
- Understanding dataset structure across multiple files
- Generating metadata specifications
- Tracking file provenance

## Basic Usage

### Opening Multiple Files

```python
from dummyxarray import DummyDataset

# Using a glob pattern
ds = DummyDataset.open_mfdataset("data/*.nc", concat_dim="time")

# Using a list of files
files = ["data_2020.nc", "data_2021.nc", "data_2022.nc"]
ds = DummyDataset.open_mfdataset(files, concat_dim="time")
```

### Querying Source Files

Once files are loaded, you can query which files contain specific coordinate ranges:

```python
# Get all tracked files
all_files = ds.get_source_files()

# Query files for a specific time range
# Note: Use coordinate types compatible with your data
files = ds.get_source_files(time=slice(None, None))
```

### Getting File Information

```python
# Get detailed information about a specific file
info = ds.get_file_info("data_2020.nc")

print(f"Coordinate range: {info['coord_range']}")
print(f"Variables: {info['metadata']['variables']}")
print(f"Dimensions: {info['metadata']['dims']}")
```

## Manual File Tracking

You can also manually track files without opening them:

```python
ds = DummyDataset()
ds.enable_file_tracking(concat_dim="time")

# Add file sources with coordinate ranges
ds.add_file_source(
    "model_run_001.nc",
    coord_range=(0, 365),
    metadata={"institution": "DKRZ", "model": "ICON"}
)

ds.add_file_source(
    "model_run_002.nc",
    coord_range=(365, 730),
    metadata={"institution": "DKRZ", "model": "ICON"}
)

# Query files
files = ds.get_source_files()
```

## File Validation

`open_mfdataset()` validates that files are compatible for concatenation:

```python
try:
    ds = DummyDataset.open_mfdataset(files, concat_dim="time")
except ValueError as e:
    print(f"Files are incompatible: {e}")
```

**Validation checks:**

- All files must have the concatenation dimension
- All files must have the same variables
- Variables must have compatible dimensions

## Properties

### `is_file_tracking_enabled`

Check if file tracking is enabled:

```python
if ds.is_file_tracking_enabled:
    print("File tracking is active")
```

### `concat_dim`

Get the concatenation dimension:

```python
print(f"Files are concatenated along: {ds.concat_dim}")
```

### `file_sources`

Access all tracked file information:

```python
for filepath, info in ds.file_sources.items():
    print(f"{filepath}: {info['coord_range']}")
```

## Important Notes

### Coordinate Type Compatibility

When querying files with `get_source_files()`, use coordinate types compatible with your data:

- If your time coordinate is `datetime64`, query with datetime objects
- If your time coordinate is numeric, query with numbers
- Type mismatches will return all files as a safe default

```python
# Example with datetime coordinates
import numpy as np

# This works if time is datetime64
files = ds.get_source_files(
    time=slice(
        np.datetime64('2020-01-01'),
        np.datetime64('2020-12-31')
    )
)

# This works if time is numeric (e.g., days since epoch)
files = ds.get_source_files(time=slice(0, 365))
```

### Metadata Only

Remember that `open_mfdataset()` only reads metadata:

- No data arrays are loaded into memory
- Coordinate values are read to determine ranges
- This keeps memory usage minimal

### File Ordering

Files are processed in the order provided (or sorted alphabetically for glob patterns):

```python
# Glob patterns are sorted
ds = DummyDataset.open_mfdataset("data/*.nc")  # Alphabetical order

# Lists maintain order
ds = DummyDataset.open_mfdataset(["file3.nc", "file1.nc", "file2.nc"])
```

## Complete Example

```python
from dummyxarray import DummyDataset
from pathlib import Path

# Open multiple climate model files
ds = DummyDataset.open_mfdataset(
    "climate_model_output/*.nc",
    concat_dim="time"
)

# Inspect the combined structure
print(ds)
print(f"\nTotal time steps: {ds.dims['time']}")
print(f"Number of files: {len(ds.file_sources)}")

# Get file information
for filepath in ds.file_sources:
    info = ds.get_file_info(filepath)
    filename = Path(filepath).name
    time_range = info['coord_range']
    print(f"\n{filename}:")
    print(f"  Time range: {time_range[0]} to {time_range[1]}")
    print(f"  Variables: {', '.join(info['metadata']['variables'])}")

# Query which files contain a specific time range
relevant_files = ds.get_source_files()
print(f"\nFiles to process: {len(relevant_files)}")
```

## API Reference

See the [API documentation](../api/dataset.md#open_mfdataset) for detailed parameter descriptions.

## See Also

- [Basic Usage](basic-usage.md) - General DummyDataset usage
- [Examples](../examples.md) - More code examples
- [API Reference](../api/dataset.md) - Complete API documentation
