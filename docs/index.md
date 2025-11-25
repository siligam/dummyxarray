# DummyXarray

A lightweight xarray-like object for building dataset metadata specifications before creating actual xarray datasets.

## Overview

dummyxarray allows you to define the structure of your dataset including dimensions, coordinates,
variables, and metadata before actually creating the xarray.Dataset with real data.
This is particularly useful for:

- **Dataset Planning**: Define your dataset structure before generating data
- **Template Generation**: Create reusable dataset templates
- **CF Compliance**: Ensure metadata follows CF conventions with automatic validation
- **Zarr Workflow**: Define chunking and compression strategies upfront
- **Metadata Validation**: Catch dimension mismatches early
- **Reproducible Workflows**: Track and replay all operations

## Key Features

### Core Functionality

✅ **Metadata-first design** - Define structure before data  
✅ **xarray compatibility** - Convert to/from xarray.Dataset  
✅ **Automatic dimension inference** - Infer from data shape  
✅ **xarray-style attribute access** - `ds.time`, `ds.temperature`  
✅ **Rich repr** - Interactive exploration in notebooks

### CF Compliance (Phase 1)

✅ **Axis detection** - Automatic X/Y/Z/T axis inference  
✅ **CF validation** - Check for CF convention compliance  
✅ **Standard names** - Support for CF standard_name vocabulary  
✅ **Dimension ordering** - Validate T, Z, Y, X ordering

### History & Provenance

✅ **Operation tracking** - Record all dataset modifications  
✅ **History export** - Export as Python, JSON, or YAML  
✅ **History visualization** - Text, DOT, or Mermaid diagrams  
✅ **Provenance tracking** - Track what changed (added/removed/modified)  
✅ **History replay** - Recreate datasets from operation history

### Data Generation & I/O

✅ **Smart data generation** - Populate with realistic random data  
✅ **Multiple formats** - Export to YAML, JSON, Zarr, NetCDF  
✅ **Template support** - Save/load dataset specifications  
✅ **Encoding support** - dtype, chunks, compression settings

### Multi-File Dataset Support (Phase 2)

✅ **Multi-file datasets** - Open multiple NetCDF files as one dataset  
✅ **Automatic frequency inference** - Detect time frequency from coordinates  
✅ **Time-based grouping** - Group datasets by decades, years, months  
✅ **File tracking** - Track which files contain which data ranges  
✅ **Metadata-only** - No data loading, only metadata operations

### Architecture

✅ **Modular design** - Mixin-based architecture for maintainability  
✅ **Well-tested** - 188 tests with comprehensive coverage  
✅ **Type-safe** - Clear API with validation

## Quick Example

```python
from dummyxarray import DummyDataset

# Create a CF-compliant dataset
ds = DummyDataset()
ds.assign_attrs(Conventions="CF-1.8", title="Climate Model Output")

# Add dimensions and coordinates
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

# Add variable with encoding
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={"standard_name": "air_temperature", "units": "K"},
    encoding={"dtype": "float32", "chunks": (6, 32, 64)}
)

# Infer CF axis attributes (X, Y, Z, T)
ds.infer_axis()
ds.set_axis_attributes()

# Validate CF compliance
result = ds.validate_cf()
print(f"Warnings: {len(result['warnings'])}")

# Populate with realistic data
ds.populate_with_random_data(seed=42)

# Export or convert
ds.save_yaml("template.yaml")
xr_dataset = ds.to_xarray()
ds.to_zarr("output.zarr")
```

## Documentation

### Getting Started

- [Installation Guide](getting-started/installation.md) - Set up dummyxarray
- [Quick Start](getting-started/quickstart.md) - Hands-on introduction

### User Guide

- [Basic Usage](user-guide/basic-usage.md) - Core concepts and workflows
- [CF Compliance](user-guide/cf-compliance.md) - Working with CF conventions
- [CF Standards](user-guide/cf-standards.md) - CF standard names and vocabulary
- [Multi-File Datasets](user-guide/mfdataset.md) - Work with multiple NetCDF files
- [History Tracking](user-guide/history-tracking.md) - Track and replay operations
- [Validation](user-guide/validation.md) - Validate dataset structure
- [Encoding](user-guide/encoding.md) - Configure chunking and compression
- [YAML Export](user-guide/yaml-export.md) - Save and load specifications
- [ncdump Import](user-guide/ncdump-import.md) - Import from ncdump output

### API Reference

- [DummyDataset](api/dataset.md) - Main dataset class
- [DummyArray](api/array.md) - Array class for variables and coordinates

### Project Architecture

- [Design Overview](architecture.md) - Mixin-based architecture
- [Testing](testing.md) - Test structure and fixtures

## Project Status

**Phase 1 Complete**: CF compliance, history tracking, and modular architecture  
**Phase 2 Complete**: Multi-file datasets, time-based grouping, CF standards  
**Future**: CMIP table integration and spatial grouping

Contributions and feedback are welcome!
