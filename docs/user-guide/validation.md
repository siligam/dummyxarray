# Validation

Learn how to validate your dataset structure to catch errors early.

## Basic Validation

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 10)
data = np.random.rand(10)
ds.add_variable("temperature", dims=["time"], data=data)

# Validate the dataset
ds.validate()  # Raises ValueError if validation fails
```

## What Gets Validated

The validation checks for:

1. **Unknown dimensions**: Variables reference dimensions that don't exist
2. **Shape mismatches**: Data shape doesn't match declared dimensions
3. **Missing coordinates** (optional): Variables use dimensions without corresponding coordinates

## Dimension Checks

```python
ds = DummyDataset()
ds.add_variable("temp", dims=["unknown_dim"])

try:
    ds.validate()
except ValueError as e:
    print(f"Error: {e}")
    # Error: Dataset validation failed:
    # temp: Unknown dimension 'unknown_dim'.
```

## Shape Validation

Shape mismatches are caught when adding variables:

```python
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)

# This will raise an error immediately
data = np.random.rand(10, 6)  # Wrong shape!
try:
    ds.add_variable("test", dims=["time", "lat"], data=data)
except ValueError as e:
    print(f"Error: {e}")
    # Error: Dimension mismatch for 'lat': existing=5 new=6
```

## Strict Coordinate Validation

Enable strict mode to require coordinates for all dimensions:

```python
ds = DummyDataset()
ds.add_dim("time", 10)
data = np.random.rand(10)
ds.add_variable("temp", dims=["time"], data=data)

# Strict validation requires coordinates
try:
    ds.validate(strict_coords=True)
except ValueError as e:
    print(f"Error: {e}")
    # Error: temp: Missing coordinate for dimension 'time'.
```

## Validation in Workflows

Validation is automatically called before conversion:

```python
# Validation happens automatically
xr_ds = ds.to_xarray(validate=True)  # Default

# Skip validation if needed (not recommended)
xr_ds = ds.to_xarray(validate=False)
```
