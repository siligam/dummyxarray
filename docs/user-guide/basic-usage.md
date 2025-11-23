# Basic Usage

This guide covers the fundamental operations in Dummy Xarray.

## Creating a Dataset

Start by importing and creating a `DummyDataset`:

```python
from dummyxarray import DummyDataset

ds = DummyDataset()
```

## Setting Global Attributes

Global attributes provide metadata about the entire dataset:

```python
ds.set_global_attrs(
    title="My Climate Dataset",
    institution="Research Institute",
    source="Model v2.0",
    Conventions="CF-1.8"
)

# You can also update attributes later
ds.set_global_attrs(experiment="historical")
```

## Defining Dimensions

Dimensions define the shape of your data:

```python
ds.add_dim("time", 365)   # 365 time steps
ds.add_dim("lat", 180)    # 180 latitude points
ds.add_dim("lon", 360)    # 360 longitude points

# Check defined dimensions
print(ds.dims)  # {'time': 365, 'lat': 180, 'lon': 360}
```

## Adding Coordinates

Coordinates are special variables that label dimension values:

```python
import numpy as np

# Time coordinate
time_values = np.arange(365)
ds.add_coord(
    "time",
    dims=["time"],
    data=time_values,
    attrs={
        "units": "days since 2020-01-01",
        "calendar": "standard",
        "long_name": "time"
    }
)

# Latitude coordinate
lat_values = np.linspace(-89.5, 89.5, 180)
ds.add_coord(
    "lat",
    dims=["lat"],
    data=lat_values,
    attrs={
        "units": "degrees_north",
        "standard_name": "latitude",
        "long_name": "latitude"
    }
)

# Longitude coordinate
lon_values = np.linspace(0.5, 359.5, 360)
ds.add_coord(
    "lon",
    dims=["lon"],
    data=lon_values,
    attrs={
        "units": "degrees_east",
        "standard_name": "longitude",
        "long_name": "longitude"
    }
)
```

## Adding Variables

Variables contain your actual data:

```python
# Create some sample data
temperature_data = np.random.rand(365, 180, 360) * 30 + 273.15

ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    data=temperature_data,
    attrs={
        "long_name": "Near-Surface Air Temperature",
        "units": "K",
        "standard_name": "air_temperature",
        "cell_methods": "time: mean"
    }
)
```

## Working Without Data

You can define the structure without providing data initially:

```python
ds = DummyDataset()
ds.add_dim("time", 12)
ds.add_dim("lat", 64)

# Define variable structure without data
ds.add_variable(
    "precipitation",
    dims=["time", "lat"],
    attrs={
        "units": "kg m-2 s-1",
        "long_name": "Precipitation Flux"
    }
)

# Export specification
ds.save_yaml("dataset_template.yaml")

# Later, load and add data
ds_loaded = DummyDataset.load_yaml("dataset_template.yaml")
precip_data = np.random.rand(12, 64)
ds_loaded.variables["precipitation"].data = precip_data
```

## Viewing Dataset Structure

```python
# As YAML
print(ds.to_yaml())

# As JSON
print(ds.to_json())

# As dictionary
spec_dict = ds.to_dict()
```

## Next Steps

- Learn about [validation](validation.md)
- Explore [encoding options](encoding.md)
- See how to [export to YAML](yaml-export.md)
