# Encoding

Configure how your data is stored with encoding parameters.

## What is Encoding?

Encoding parameters control how data is written to disk formats like Zarr or NetCDF. This includes:

- Data type (dtype)
- Chunking strategy
- Compression
- Fill values
- Scale factors

## Basic Encoding

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 100)

data = np.random.rand(100)
ds.add_variable(
    "temperature",
    dims=["time"],
    data=data,
    encoding={
        "dtype": "float32",  # Store as 32-bit float
    }
)
```

## Chunking

Chunking is crucial for performance with large datasets:

```python
ds = DummyDataset()
ds.add_dim("time", 365)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

data = np.random.rand(365, 180, 360)
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    data=data,
    encoding={
        "dtype": "float32",
        "chunks": (30, 90, 180),  # Chunk size for each dimension
    }
)
```

## Compression

Add compression to reduce file size:

```python
import zarr

ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    data=data,
    encoding={
        "dtype": "float32",
        "chunks": (30, 90, 180),
        "compressor": zarr.Blosc(cname='zstd', clevel=3, shuffle=2)
    }
)
```

## Fill Values

Specify fill values for missing data:

```python
ds.add_variable(
    "temperature",
    dims=["time"],
    data=data,
    encoding={
        "dtype": "float32",
        "_FillValue": -9999.0
    }
)
```

## Scale and Offset

Use scale_factor and add_offset for packed data:

```python
ds.add_variable(
    "temperature",
    dims=["time"],
    data=data,
    encoding={
        "dtype": "int16",
        "scale_factor": 0.01,
        "add_offset": 273.15,
        "_FillValue": -32768
    }
)
```

## Encoding for Coordinates

Coordinates can also have encoding:

```python
time_data = np.arange(365)
ds.add_coord(
    "time",
    dims=["time"],
    data=time_data,
    attrs={"units": "days since 2020-01-01"},
    encoding={
        "dtype": "int32",
        "calendar": "standard"
    }
)
```

## Best Practices

### Chunking Strategy

- **Time series data**: Large chunks in time, smaller in space
- **Spatial data**: Smaller chunks in time, larger in space
- **General rule**: Aim for chunk sizes of 10-100 MB

```python
# For time series analysis
encoding={"chunks": (365, 45, 90)}  # Full year, quarter lat/lon

# For spatial analysis
encoding={"chunks": (1, 180, 360)}  # Single time, full spatial
```

### Data Types

- Use `float32` instead of `float64` when precision allows
- Use `int16` or `int32` for integer data
- Consider packed integers with scale/offset for large datasets

### Compression

- `zstd` (level 3): Good balance of speed and compression
- `lz4`: Fastest, moderate compression
- `blosc`: Good for scientific data

## Applying Encoding

Encoding is automatically applied when converting to xarray or writing to Zarr:

```python
# Encoding is preserved in xarray
xr_ds = ds.to_xarray()
print(xr_ds["temperature"].encoding)

# Encoding is used when writing to Zarr
ds.to_zarr("output.zarr")
```
