# Examples

This page contains comprehensive examples demonstrating the features of Dummy Xarray.

## Basic Metadata-Only Dataset

Create a dataset specification without any data:

```python
from dummyxarray import DummyDataset

ds = DummyDataset()

# Set global attributes
ds.set_global_attrs(
    title="Test Climate Dataset",
    institution="DKRZ",
    experiment="historical",
    source="Example Model v1.0"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

# Add coordinates (without data for now)
ds.add_coord("time", ["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

# Add variables (without data)
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    attrs={"long_name": "Near-Surface Air Temperature", "units": "K"}
)

# Export to YAML for documentation
print(ds.to_yaml())
ds.save_yaml("dataset_spec.yaml")
```

## Automatic Dimension Inference

Let dimensions be inferred from your data:

```python
import numpy as np
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.set_global_attrs(title="Auto-inferred Dataset")

# Create data with specific shape
temp_data = np.random.rand(12, 64, 128)

# Add variable with data - dimensions will be auto-inferred
ds.add_variable(
    "tas",
    data=temp_data,
    attrs={"units": "K", "long_name": "air_temperature"}
)

print("Dimensions were automatically inferred:")
print(ds.dims)  # {'dim_0': 12, 'dim_1': 64, 'dim_2': 128}
```

## With Encoding for Zarr/NetCDF

Specify encoding parameters for optimal storage:

```python
import numpy as np
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.set_global_attrs(title="Dataset with Encoding")

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

# Add coordinate with encoding
time_data = np.arange(12)
ds.add_coord(
    "time",
    ["time"],
    data=time_data,
    attrs={"units": "days since 2000-01-01"},
    encoding={"dtype": "int32"}
)

# Add variable with chunking and compression
temp_data = np.random.rand(12, 64, 128) * 20 + 273.15
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    data=temp_data,
    attrs={"long_name": "Near-Surface Air Temperature", "units": "K"},
    encoding={
        "dtype": "float32",
        "chunks": (6, 32, 64),
        "compressor": None,  # Can use zarr.Blosc() or similar
    }
)

# Validate and write to Zarr
ds.validate()
ds.to_zarr("output.zarr")
```

## Loading and Modifying Specifications

Save and load dataset specifications:

```python
from dummyxarray import DummyDataset

# Create and save a specification
ds = DummyDataset()
ds.set_global_attrs(title="Template Dataset")
ds.add_dim("time", 12)
ds.add_variable("temperature", ["time"], attrs={"units": "K"})
ds.save_yaml("template.yaml")

# Load it later
loaded_ds = DummyDataset.load_yaml("template.yaml")

# Modify and use
loaded_ds.set_global_attrs(experiment="run_001")
print(loaded_ds.to_yaml())
```

## Validation Example

Catch errors early with validation:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)

# Add variable with correct shape
data = np.random.rand(10, 5)
ds.add_variable("test", dims=["time", "lat"], data=data)

# Validate - should pass
try:
    ds.validate()
    print("✓ Validation passed!")
except ValueError as e:
    print(f"✗ Validation failed: {e}")

# Try adding a variable with wrong dimension
ds2 = DummyDataset()
ds2.add_variable("bad_var", dims=["unknown_dim"])

try:
    ds2.validate()
except ValueError as e:
    print(f"✗ Caught error: {e}")
```

## Complete Workflow

A complete example from specification to xarray:

```python
import numpy as np
from dummyxarray import DummyDataset

# 1. Create specification
ds = DummyDataset()
ds.set_global_attrs(
    title="Complete Example",
    institution="Research Center",
    Conventions="CF-1.8"
)

# 2. Define structure
ds.add_dim("time", 365)
ds.add_dim("lat", 90)
ds.add_dim("lon", 180)

# 3. Add coordinates with data
time_data = np.arange(365)
lat_data = np.linspace(-90, 90, 90)
lon_data = np.linspace(-180, 180, 180)

ds.add_coord("time", ["time"], data=time_data, 
             attrs={"units": "days since 2020-01-01"})
ds.add_coord("lat", ["lat"], data=lat_data,
             attrs={"units": "degrees_north", "standard_name": "latitude"})
ds.add_coord("lon", ["lon"], data=lon_data,
             attrs={"units": "degrees_east", "standard_name": "longitude"})

# 4. Add variables with encoding
temp_data = np.random.rand(365, 90, 180) * 20 + 273.15
ds.add_variable(
    "temperature",
    ["time", "lat", "lon"],
    data=temp_data,
    attrs={
        "long_name": "Near-Surface Air Temperature",
        "units": "K",
        "standard_name": "air_temperature"
    },
    encoding={
        "dtype": "float32",
        "chunks": (30, 45, 90)
    }
)

# 5. Validate
ds.validate()

# 6. Convert to xarray
xr_ds = ds.to_xarray()
print(xr_ds)

# 7. Write to Zarr
ds.to_zarr("complete_example.zarr")
```

## Extract Metadata from Existing xarray Dataset

Create a template from an existing dataset:

```python
import xarray as xr
from dummyxarray import DummyDataset

# Load an existing xarray dataset
existing_ds = xr.open_dataset("my_data.nc")

# Extract metadata only (no data)
dummy_ds = DummyDataset.from_xarray(existing_ds, include_data=False)

# Save as a reusable template
dummy_ds.save_yaml("template.yaml")

# Or extract with data included
dummy_with_data = DummyDataset.from_xarray(existing_ds, include_data=True)
```

## Populate with Random Data for Testing

Generate meaningful random data based on metadata:

```python
from dummyxarray import DummyDataset

# Create structure without data
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)
ds.add_dim("lon", 8)

ds.add_coord("time", ["time"], attrs={"units": "days"})
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

ds.add_variable("temperature", ["time", "lat", "lon"], 
                attrs={"units": "K", "standard_name": "air_temperature"})
ds.add_variable("precipitation", ["time", "lat", "lon"],
                attrs={"units": "kg m-2 s-1"})

# Populate all coordinates and variables with meaningful random data
ds.populate_with_random_data(seed=42)  # seed for reproducibility

# Check the generated data
print(f"Temperature range: {ds.variables['temperature'].data.min():.1f} - "
      f"{ds.variables['temperature'].data.max():.1f} K")
print(f"Latitude range: {ds.coords['lat'].data.min():.1f} - "
      f"{ds.coords['lat'].data.max():.1f}°")

# Convert to xarray and use for testing
xr_ds = ds.to_xarray()
```

## xarray-style Attribute Access

Access coordinates and variables using dot notation:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_coord("time", ["time"], attrs={"units": "days"})
ds.add_variable("temperature", ["time"], attrs={"units": "K"})

# Access using attribute notation (like xarray)
print(ds.time)                  # Access coordinate
print(ds.temperature)           # Access variable

# Modify via attribute access
ds.time.data = np.arange(10)
ds.time.attrs["standard_name"] = "time"
ds.time.attrs["calendar"] = "gregorian"

# Rich repr shows structure clearly
print(ds)
# Output shows:
# <dummyxarray.DummyDataset>
# Dimensions:
#   time: 10
# Coordinates:
#   ✓ time                 (time)               int64
# Data variables:
#   ✗ temperature          (time)               ?

# Inspect individual arrays
print(ds.time)
# Output:
# <dummyxarray.DummyArray>
# Dimensions: (time)
# Shape: (10,)
# dtype: int64
# Data: [0 1 2 3 4 5 6 7 8 9]
# Attributes:
#     units: days
#     standard_name: time
#     calendar: gregorian
```

## More Examples

For more examples, check out the example files in the repository:

- `example.py` - Basic usage and core features
- `example_from_xarray.py` - Extracting metadata from xarray datasets
- `example_populate.py` - Data population with random data
- Basic usage examples
- Automatic dimension inference
- Encoding specifications
- Validation demonstrations
- xarray conversion
- Zarr writing
- YAML save/load
