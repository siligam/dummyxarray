# DummyArray

Represents a single array (variable or coordinate) with metadata.

## Overview

`DummyArray` is used for both coordinates and variables in a `DummyDataset`. Each array contains:

- **Dimensions** - List of dimension names
- **Attributes** - Metadata dictionary
- **Data** - Optional numpy array
- **Encoding** - Encoding parameters (dtype, chunks, compression)

## Key Features

- Automatic dimension inference from data shape
- xarray-compatible attribute assignment
- History tracking (if enabled)
- Rich repr for interactive exploration

## Usage

```python
from dummyxarray import DummyArray
import numpy as np

# Create array with dimensions
arr = DummyArray(dims=["time", "lat", "lon"])

# Set attributes
arr.assign_attrs(
    standard_name="air_temperature",
    units="K",
    long_name="Air Temperature"
)

# Add data
arr.data = np.random.rand(10, 64, 128)

# Set encoding
arr.encoding = {
    "dtype": "float32",
    "chunks": (5, 32, 64),
    "compressor": "zstd"
}
```

## API Reference

::: dummyxarray.DummyArray
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
