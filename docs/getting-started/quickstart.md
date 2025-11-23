# Quick Start

This guide will walk you through the basic usage of Dummy Xarray.

## Creating Your First Dataset

```python
from dummyxarray import DummyDataset

# Create an empty dataset
ds = DummyDataset()

# Set global attributes
ds.set_global_attrs(
    title="My First Dataset",
    institution="Research Institute",
    experiment="test_run"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

print("Dataset created with dimensions:", ds.dims)
```

## Adding Coordinates

```python
import numpy as np

# Add time coordinate
time_data = np.arange(12)
ds.add_coord(
    "time",
    dims=["time"],
    data=time_data,
    attrs={"units": "months since 2000-01-01", "calendar": "standard"}
)

# Add latitude coordinate
lat_data = np.linspace(-90, 90, 64)
ds.add_coord(
    "lat",
    dims=["lat"],
    data=lat_data,
    attrs={"units": "degrees_north", "standard_name": "latitude"}
)

# Add longitude coordinate
lon_data = np.linspace(-180, 180, 128)
ds.add_coord(
    "lon",
    dims=["lon"],
    data=lon_data,
    attrs={"units": "degrees_east", "standard_name": "longitude"}
)
```

## Adding Variables

```python
# Add a temperature variable with data
temp_data = np.random.rand(12, 64, 128) * 20 + 273.15

ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    data=temp_data,
    attrs={
        "long_name": "Near-Surface Air Temperature",
        "units": "K",
        "standard_name": "air_temperature"
    }
)
```

## Exporting to YAML

```python
# View the dataset structure
print(ds.to_yaml())

# Save to file
ds.save_yaml("my_dataset_spec.yaml")
```

## Converting to xarray

```python
# Convert to a real xarray.Dataset
xr_dataset = ds.to_xarray()
print(xr_dataset)
```

## Writing to Zarr

```python
# Write directly to Zarr format
ds.to_zarr("output.zarr")

# Load it back with xarray
import xarray as xr
loaded = xr.open_zarr("output.zarr")
```

## Automatic Dimension Inference

If you provide data without specifying dimensions, they will be inferred automatically:

```python
ds2 = DummyDataset()

# Dimensions will be auto-generated as dim_0, dim_1, dim_2
data = np.random.rand(10, 20, 30)
ds2.add_variable("my_var", data=data)

print(ds2.dims)  # {'dim_0': 10, 'dim_1': 20, 'dim_2': 30}
```

## Next Steps

- Learn about [validation](../user-guide/validation.md)
- Explore [encoding options](../user-guide/encoding.md)
- Check out the [API reference](../api/dataset.md)
