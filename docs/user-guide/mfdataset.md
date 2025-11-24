# Multi-file Dataset Support

The `open_mfdataset()` feature allows you to work with multiple NetCDF files as a single dataset,
tracking which files contain specific coordinate ranges. This is particularly useful for large climate
datasets split across multiple files.

## Overview

Unlike xarray's `open_mfdataset()` which loads data into memory, DummyDataset's version only reads
**metadata** from files. This makes it ideal for:

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

## Automatic Frequency Inference

When opening files with time coordinates, DummyDataset automatically infers and stores the time
frequency in the coordinate attributes:

```python
# Open files with time coordinates
ds = DummyDataset.open_mfdataset("hourly_*.nc", concat_dim="time")

# Frequency is automatically detected and stored
print(ds.coords['time'].attrs['frequency'])  # "1H"

# Works with various frequencies
# - Hourly: "1H", "3H", "6H", "12H"
# - Daily: "1D"
# - Monthly: "1M"
# - Sub-hourly: "15T" (minutes), "30S" (seconds)
```

**Requirements for frequency inference:**

- Time coordinate must have CF-compliant `units` attribute (e.g., "hours since 2000-01-01")
- Time values must be regularly spaced
- At least 2 time values in the coordinate

**Calendar support:**

The frequency inference respects the `calendar` attribute if present, supporting all cftime calendars:

- `standard` (Gregorian, default)
- `noleap` (365-day)
- `360_day`
- `julian`
- And all other cftime calendars

## Time-Based Grouping

Once files are opened with frequency inference, you can group the dataset by time periods using
`groupby_time()`. This creates multiple metadata-only datasets, each representing a time period:

```python
# Open 100 years of hourly data
ds = DummyDataset.open_mfdataset("hourly_*.nc", concat_dim="time")

# Group into decades
decades = ds.groupby_time('10Y')

print(f"Number of decades: {len(decades)}")  # 10

# Each decade is a separate DummyDataset
decade_0 = decades[0]
print(decade_0.coords['time'].attrs['units'])
# "hours since 2000-01-01 00:00:00"

print(decade_0.dims['time'])
# ~87600 (10 years * 365.25 days * 24 hours)
```

### Supported Grouping Frequencies

```python
# Years
decades = ds.groupby_time('10Y')
quinquennials = ds.groupby_time('5Y')
annual = ds.groupby_time('1Y')

# Months
quarterly = ds.groupby_time('3M')
monthly = ds.groupby_time('1M')

# Days
weekly = ds.groupby_time('7D')
daily = ds.groupby_time('1D')

# Hours (for high-frequency data)
six_hourly = ds.groupby_time('6H')
```

### Unit Normalization

By default, `groupby_time()` normalizes the time units for each group to start at the group's
beginning:

```python
# With normalization (default)
decades = ds.groupby_time('10Y', normalize_units=True)
print(decades[0].coords['time'].attrs['units'])
# "hours since 2000-01-01 00:00:00"

print(decades[1].coords['time'].attrs['units'])
# "hours since 2010-01-01 00:00:00"

# Without normalization (keeps original units)
decades = ds.groupby_time('10Y', normalize_units=False)
# All groups keep the original units from the first file
```

### File Tracking in Groups

File tracking information is preserved in grouped datasets:

```python
decades = ds.groupby_time('10Y')

# Query which files are in the first decade
files = decades[0].get_source_files()
print(f"Files in decade 0: {files}")
# ['hourly_2000.nc', 'hourly_2001.nc', ..., 'hourly_2009.nc']
```

### Use Cases

**Climate data analysis planning:**

```python
# Open century of daily climate data
ds = DummyDataset.open_mfdataset("tas_day_*.nc", concat_dim="time")

# Group into decades for analysis
decades = ds.groupby_time('10Y')

# Plan processing for each decade
for i, decade in enumerate(decades):
    start_year = 1900 + i * 10
    print(f"Decade {start_year}s:")
    print(f"  Time steps: {decade.dims['time']}")
    print(f"  Files: {len(decade.get_source_files())}")
    print(f"  Variables: {list(decade.variables.keys())}")
```

**Seasonal grouping:**

```python
# Open annual data
ds = DummyDataset.open_mfdataset("data_*.nc", concat_dim="time")

# Group by season (3 months)
seasons = ds.groupby_time('3M')

# Process each season
for i, season in enumerate(seasons):
    season_name = ['DJF', 'MAM', 'JJA', 'SON'][i % 4]
    print(f"{season_name}: {season.dims['time']} timesteps")
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
