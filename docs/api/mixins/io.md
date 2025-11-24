# IOMixin

Provides serialization and format conversion functionality.

## Overview

The `IOMixin` enables exporting and importing datasets in multiple formats:

- **YAML** - Human-readable configuration format
- **JSON** - Structured data format
- **xarray** - Convert to/from xarray.Dataset
- **Zarr** - Write directly to Zarr storage
- **NetCDF** - Via xarray conversion

## Key Methods

### Export Methods

- `to_dict()` - Export as Python dictionary
- `to_json(indent=2, **kwargs)` - Export as JSON string
- `to_yaml()` - Export as YAML string
- `save_yaml(filepath)` - Save to YAML file
- `to_xarray()` - Convert to xarray.Dataset
- `to_zarr(store, **kwargs)` - Write to Zarr store

### Import Methods

- `from_xarray(xr_dataset)` - Create from xarray.Dataset (class method)
- `load_yaml(filepath)` - Load from YAML file (class method)

## Usage

```python
# Export to YAML
ds.save_yaml("template.yaml")

# Load from YAML
ds = DummyDataset.load_yaml("template.yaml")

# Convert to xarray
xr_ds = ds.to_xarray()

# Import from xarray
ds = DummyDataset.from_xarray(xr_ds)

# Write to Zarr
ds.to_zarr("output.zarr")
```

## API Reference

::: dummyxarray.io.IOMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
