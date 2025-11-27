# Intake Catalogs

dummyxarray provides comprehensive support for Intake catalogs, allowing you to both export 
dataset specifications to Intake catalog format and import existing Intake catalogs back 
into DummyDataset objects. This enables complete round-trip compatibility with the Intake 
data cataloging ecosystem.

## Overview

Intake is a data cataloging system that provides a unified interface for discovering 
and accessing data. dummyxarray's Intake catalog support allows you to:

- **Export** DummyDataset structures to Intake catalog YAML files
- **Import** Intake catalogs to recreate DummyDataset objects
- **Preserve** complete metadata including dimensions, coordinates, variables, and encoding
- **Integrate** with the broader Intake ecosystem for data discovery and sharing

## Exporting to Intake Catalogs

### Basic Export

```python
from dummyxarray import DummyDataset

# Create a dataset
ds = DummyDataset()
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)
ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={"units": "K", "standard_name": "air_temperature"},
    encoding={"dtype": "float32", "chunks": [6, 32, 64]}
)

# Generate catalog YAML string
catalog_yaml = ds.to_intake_catalog()
print(catalog_yaml)
```

### Customized Export

```python
# Export with custom parameters
catalog_yaml = ds.to_intake_catalog(
    name="climate_data",
    description="Climate model output with temperature and precipitation",
    driver="zarr",
    data_path="data/climate_model_output.zarr",
    chunks={"time": 6}  # Additional driver arguments
)
```

### Save to File

```python
# Save catalog directly to file
ds.save_intake_catalog(
    "catalog.yaml",
    name="climate_data",
    description="Climate model output",
    driver="zarr",
    data_path="data/climate.zarr"
)
```

## Catalog Structure

The generated Intake catalog includes:

```yaml
metadata:
  version: 1
  description: Intake catalog for climate_data
  dataset_attrs:
    title: Climate Model Output
    institution: Example Climate Center
    Conventions: CF-1.8

sources:
  climate_data:
    description: Climate model output with temperature and precipitation
    driver: zarr
    args:
      urlpath: data/climate_model_output.zarr
    metadata:
      dimensions:
        time: 12
        lat: 180
        lon: 360
      coordinates:
        time:
          dims: [time]
          attrs:
            units: days since 2000-01-01
      variables:
        temperature:
          dims: [time, lat, lon]
          attrs:
            units: K
            standard_name: air_temperature
          encoding:
            dtype: float32
            chunks: [6, 32, 64]
```

## Importing from Intake Catalogs

### Load from File

```python
# Load from catalog file
loaded_ds = DummyDataset.from_intake_catalog("catalog.yaml", "climate_data")

# Or use the convenience method
loaded_ds = DummyDataset.load_intake_catalog("catalog.yaml", "climate_data")
```

### Load from Dictionary

```python
import yaml

# Load catalog YAML and parse to dictionary
with open("catalog.yaml") as f:
    catalog_dict = yaml.safe_load(f)

# Create DummyDataset from dictionary
loaded_ds = DummyDataset.from_intake_catalog(catalog_dict, "climate_data")
```

### Automatic Source Selection

```python
# If catalog contains only one source, you can omit the source name
single_source_ds = DummyDataset.from_intake_catalog("single_source_catalog.yaml")
```

## Round-Trip Workflow

Create a complete round-trip workflow:

```python
from dummyxarray import DummyDataset
import tempfile
import yaml

# 1. Create original dataset
original_ds = DummyDataset()
original_ds.assign_attrs(
    title="Climate Model Output",
    institution="Example Climate Center",
    Conventions="CF-1.8"
)
original_ds.add_dim("time", 12)
original_ds.add_dim("lat", 180)
original_ds.add_dim("lon", 360)
original_ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
original_ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={"units": "K"},
    encoding={"dtype": "float32"}
)

# 2. Export to catalog
catalog_yaml = original_ds.to_intake_catalog(
    name="climate_data",
    description="Climate model output",
    driver="zarr"
)

# 3. Save to temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    catalog_path = f.name
    f.write(catalog_yaml)

# 4. Load from catalog
restored_ds = DummyDataset.from_intake_catalog(catalog_path, "climate_data")

# 5. Verify round-trip integrity
assert restored_ds.dims == original_ds.dims
assert set(restored_ds.variables.keys()) == set(original_ds.variables.keys())
assert restored_ds.attrs["title"] == original_ds.attrs["title"]

print("Round-trip successful!")
```

## Advanced Features

### Multiple Sources in Catalog

When working with catalogs containing multiple data sources:

```python
# Catalog with multiple sources
multi_source_catalog = {
    "metadata": {"version": 1},
    "sources": {
        "temperature": {
            "driver": "zarr",
            "args": {"urlpath": "data/temperature.zarr"},
            "metadata": {"dimensions": {"time": 12, "lat": 180, "lon": 360}}
        },
        "precipitation": {
            "driver": "zarr", 
            "args": {"urlpath": "data/precipitation.zarr"},
            "metadata": {"dimensions": {"time": 12, "lat": 180, "lon": 360}}
        }
    }
}

# Must specify which source to load
temp_ds = DummyDataset.from_intake_catalog(multi_source_catalog, "temperature")
precip_ds = DummyDataset.from_intake_catalog(multi_source_catalog, "precipitation")
```

### Driver Configuration

Different data formats and drivers:

```python
# NetCDF driver
ds.to_intake_catalog(
    name="netcdf_data",
    driver="netcdf",
    data_path="data/output.nc",
    engine="netcdf4"
)

# Xarray driver with custom arguments
ds.to_intake_catalog(
    name="xarray_data", 
    driver="xarray",
    data_path="data/*.nc",
    combine="by_coords",
    parallel=True
)
```

### Metadata Preservation

All dataset metadata is preserved in the catalog:

```python
# Dataset attributes become catalog metadata
ds.assign_attrs(
    title="My Dataset",
    institution="My Organization",
    project="Climate Research",
    version="1.0"
)

# After round-trip, attributes are preserved
loaded_ds = DummyDataset.from_intake_catalog("catalog.yaml", "my_data")
assert loaded_ds.attrs["title"] == "My Dataset"
assert loaded_ds.attrs["institution"] == "My Organization"

# Catalog-specific attributes are also added
assert loaded_ds.attrs["intake_catalog_source"] == "my_data"
assert loaded_ds.attrs["intake_driver"] == "zarr"
```

## Error Handling

The import functionality includes comprehensive error handling:

```python
try:
    # File not found
    ds = DummyDataset.from_intake_catalog("nonexistent.yaml")
except FileNotFoundError as e:
    print(f"Catalog file not found: {e}")

try:
    # Invalid catalog format
    ds = DummyDataset.from_intake_catalog({"invalid": "structure"})
except ValueError as e:
    print(f"Invalid catalog: {e}")

try:
    # Source not found in multi-source catalog
    ds = DummyDataset.from_intake_catalog(multi_source_catalog, "nonexistent_source")
except ValueError as e:
    print(f"Source not found: {e}")
```

## Integration with Intake Ecosystem

The generated catalogs are fully compatible with the Intake ecosystem:

```python
import intake

# Load catalog with Intake
catalog = intake.open_catalog("catalog.yaml")

# Access data source
data_source = catalog.climate_data

# Get metadata
print(data_source.description)
print(data_source.metadata)

# Load actual data (when available)
# ds = data_source.read()
```

## Best Practices

1. **Descriptive Names**: Use meaningful source names that reflect the data content
2. **Complete Metadata**: Include comprehensive dataset attributes for better discoverability
3. **Consistent Paths**: Use relative paths with `{{ CATALOG_DIR }}` template for portability
4. **Driver Selection**: Choose appropriate drivers for your data format and access patterns
5. **Version Control**: Track catalog files alongside your code for reproducibility

## Examples

See the [Intake Catalog Example](
https://github.com/siligam/dummyxarray/blob/main/examples/intake_catalog_example.py
) for a complete working demonstration of round-trip catalog functionality.
