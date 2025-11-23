# YAML Export

Export and import dataset specifications using YAML format.

## Exporting to YAML

```python
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.set_global_attrs(title="My Dataset")
ds.add_dim("time", 12)
ds.add_variable("temperature", ["time"], attrs={"units": "K"})

# Get YAML string
yaml_str = ds.to_yaml()
print(yaml_str)

# Save to file
ds.save_yaml("dataset_spec.yaml")
```

## YAML Structure

The exported YAML contains:

```yaml
dimensions:
  time: 12
  lat: 64
  lon: 128
coordinates:
  time:
    dims:
    - time
    attrs:
      units: days since 2000-01-01
    encoding:
      dtype: int32
    has_data: true
variables:
  temperature:
    dims:
    - time
    - lat
    - lon
    attrs:
      long_name: Temperature
      units: K
    encoding:
      dtype: float32
      chunks: [6, 32, 64]
    has_data: true
attrs:
  title: My Dataset
  institution: DKRZ
```

## Loading from YAML

```python
from dummyxarray import DummyDataset

# Load specification
ds = DummyDataset.load_yaml("dataset_spec.yaml")

# The structure is loaded, but not the data
print(ds.dims)
print(ds.variables.keys())

# Add data later
import numpy as np
ds.variables["temperature"].data = np.random.rand(12, 64, 128)

# Convert to xarray
xr_ds = ds.to_xarray()
```

## Use Cases

### 1. Documentation

Export dataset specifications for documentation:

```python
ds.save_yaml("docs/dataset_specification.yaml")
```

### 2. Templates

Create reusable templates:

```python
# Create template
template = DummyDataset()
template.set_global_attrs(Conventions="CF-1.8")
template.add_dim("time", None)  # Placeholder
template.add_variable("temperature", ["time"], attrs={"units": "K"})
template.save_yaml("templates/temperature_timeseries.yaml")

# Use template
ds = DummyDataset.load_yaml("templates/temperature_timeseries.yaml")
ds.dims["time"] = 365  # Set actual size
```

### 3. Version Control

Track dataset structure changes in git:

```bash
git add dataset_spec.yaml
git commit -m "Update dataset structure"
```

### 4. Collaboration

Share specifications with collaborators:

```python
# Person A creates spec
ds = DummyDataset()
ds.set_global_attrs(title="Shared Dataset")
ds.add_dim("time", 100)
ds.save_yaml("shared_spec.yaml")

# Person B loads and uses
ds_loaded = DummyDataset.load_yaml("shared_spec.yaml")
# Add their data...
```

## JSON Export

You can also export to JSON:

```python
# Get JSON string
json_str = ds.to_json()

# Or as dictionary
spec_dict = ds.to_dict()
```

## Limitations

Note that the actual data arrays are not saved to YAML, only the metadata and structure. The `has_data` field indicates whether data was present when the spec was created.
