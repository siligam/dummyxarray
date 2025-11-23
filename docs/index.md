# Dummy Xarray

A lightweight xarray-like object for building dataset metadata specifications before creating actual xarray datasets.

## Overview

Dummy Xarray allows you to define the structure of your dataset including dimensions, coordinates, variables, and metadata before actually creating the xarray.Dataset with real data. This is particularly useful for:

- **Dataset Planning**: Define your dataset structure before generating data
- **Template Generation**: Create reusable dataset templates
- **CF-Compliance Preparation**: Set up all required metadata before creating datasets
- **Zarr Workflow**: Define chunking and compression strategies upfront
- **Metadata Validation**: Catch dimension mismatches early

## Key Features

✅ **Define dimensions and their sizes**  
✅ **Add variables and coordinates with metadata**  
✅ **Automatic dimension inference from data**  
✅ **Export to YAML/JSON for documentation**  
✅ **Save/load specifications from YAML files**  
✅ **Support for encoding** (dtype, chunks, compression)  
✅ **Dataset validation** (dimension checks, shape matching)  
✅ **Convert to real xarray.Dataset**  
✅ **Write directly to Zarr format**

## Quick Example

```python
from dummyxarray import DummyDataset
import numpy as np

# Create a dataset
ds = DummyDataset()

# Set global attributes
ds.set_global_attrs(
    title="Climate Model Output",
    institution="DKRZ"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

# Add a variable with metadata
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={
        "long_name": "Near-Surface Air Temperature",
        "units": "K",
        "standard_name": "air_temperature"
    }
)

# Export to YAML for documentation
print(ds.to_yaml())

# Later, add data and convert to xarray
data = np.random.rand(12, 180, 360)
ds.variables["temperature"].data = data
xr_dataset = ds.to_xarray()
```

## Getting Started

Check out the [Installation Guide](getting-started/installation.md) to get started, or jump straight to the [Quick Start](getting-started/quickstart.md) for a hands-on introduction.

## Project Status

This project is under active development. Contributions and feedback are welcome!
