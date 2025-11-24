# CF Compliance

dummyxarray provides comprehensive support for CF (Climate and Forecast) conventions, helping you create metadata-compliant datasets.

## Overview

The CF conventions define standard metadata for climate and forecast data. dummyxarray helps you:

- **Detect axis types** automatically (X, Y, Z, T)
- **Validate** datasets against CF conventions
- **Set standard attributes** following CF guidelines
- **Check dimension ordering** (recommended: T, Z, Y, X)

## Axis Detection

### Automatic Inference

dummyxarray can automatically infer axis types based on:
- Coordinate names (time, lat, lon, lev, etc.)
- Units attributes (degrees_north, degrees_east, days since, etc.)
- Standard_name attributes (latitude, longitude, time, etc.)

```python
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

# Add coordinates with CF-compliant attributes
ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

# Infer axis types
axes = ds.infer_axis()
print(axes)
# Output: {'time': 'T', 'lat': 'Y', 'lon': 'X'}
```

### Setting Axis Attributes

Once axes are inferred, you can set them on the coordinates:

```python
# Set axis attributes on all coordinates
ds.set_axis_attributes()

# Check the result
print(ds.coords["time"].attrs["axis"])  # 'T'
print(ds.coords["lat"].attrs["axis"])   # 'Y'
print(ds.coords["lon"].attrs["axis"])   # 'X'
```

### Inference Rules

#### Time Axis (T)
- **Names**: time, t, date
- **Units**: Contains "since", "days", "hours", "minutes", "seconds"
- **Standard names**: time

#### Latitude Axis (Y)
- **Names**: lat, latitude, y, j, yc
- **Units**: degrees_north, degree_north
- **Standard names**: latitude, projection_y_coordinate, grid_latitude

#### Longitude Axis (X)
- **Names**: lon, longitude, x, i, xc
- **Units**: degrees_east, degree_east
- **Standard names**: longitude, projection_x_coordinate, grid_longitude

#### Vertical Axis (Z)
- **Names**: lev, level, plev, height, depth, alt, z, k
- **Units**: pa, hpa, mbar, m, km, level, sigma
- **Standard names**: altitude, height, depth, air_pressure, model_level_number

## CF Validation

### Basic Validation

Check your dataset for CF compliance issues:

```python
# Validate the dataset
result = ds.validate_cf()

# Check for errors and warnings
print(f"Errors: {len(result['errors'])}")
print(f"Warnings: {len(result['warnings'])}")

# Print warnings
for warning in result['warnings']:
    print(f"  - {warning}")
```

### Validation Checks

The validator checks for:

1. **Missing axis attributes** - Coordinates without axis attribute
2. **Missing units** - Coordinates/variables without units
3. **Missing standard_name** - Coordinates without standard_name
4. **Missing Conventions** - Global attribute not set
5. **Dimension ordering** - Not following T, Z, Y, X recommendation
6. **Missing long_name** - Variables without descriptive name

### Strict Mode

Use strict mode to raise an error on any CF violation:

```python
try:
    ds.validate_cf(strict=True)
except ValueError as e:
    print(f"CF validation failed: {e}")
```

## Complete CF-Compliant Example

Here's a complete example creating a CF-compliant dataset:

```python
from dummyxarray import DummyDataset

# Create dataset with CF conventions
ds = DummyDataset()
ds.assign_attrs(
    Conventions="CF-1.8",
    title="Example CF-Compliant Dataset",
    institution="Example Institution",
    source="dummyxarray example",
    history="Created with dummyxarray"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lev", 5)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

# Add coordinates with full CF metadata
ds.add_coord(
    "time",
    dims=["time"],
    attrs={
        "standard_name": "time",
        "long_name": "time",
        "units": "days since 2000-01-01 00:00:00",
        "calendar": "gregorian"
    }
)

ds.add_coord(
    "lev",
    dims=["lev"],
    attrs={
        "standard_name": "air_pressure",
        "long_name": "pressure level",
        "units": "hPa",
        "positive": "down"
    }
)

ds.add_coord(
    "lat",
    dims=["lat"],
    attrs={
        "standard_name": "latitude",
        "long_name": "latitude",
        "units": "degrees_north"
    }
)

ds.add_coord(
    "lon",
    dims=["lon"],
    attrs={
        "standard_name": "longitude",
        "long_name": "longitude",
        "units": "degrees_east"
    }
)

# Infer and set axis attributes
ds.infer_axis()
ds.set_axis_attributes()

# Add variable with CF metadata
ds.add_variable(
    "temperature",
    dims=["time", "lev", "lat", "lon"],
    attrs={
        "standard_name": "air_temperature",
        "long_name": "Air Temperature",
        "units": "K",
        "cell_methods": "time: mean"
    }
)

# Validate
result = ds.validate_cf()
if result['warnings']:
    print("Warnings:")
    for warning in result['warnings']:
        print(f"  - {warning}")
else:
    print("✓ Dataset is CF-compliant!")

# Populate with data
ds.populate_with_random_data(seed=42)

# Export
ds.save_yaml("cf_compliant_template.yaml")
xr_ds = ds.to_xarray()
```

## Query Axis Coordinates

Find all coordinates with a specific axis:

```python
# Get all X-axis coordinates
x_coords = ds.get_axis_coordinates("X")
print(f"X-axis coordinates: {x_coords}")

# Get all time coordinates
t_coords = ds.get_axis_coordinates("T")
print(f"Time coordinates: {t_coords}")
```

## Resetting History

After importing from xarray or making many changes, you can reset the history:

```python
# Import from existing xarray dataset
import xarray as xr
xr_ds = xr.open_dataset("existing_data.nc")
ds = DummyDataset.from_xarray(xr_ds)

# Reset history to start fresh
ds.reset_history()

# Now only track new modifications
ds.infer_axis()
ds.set_axis_attributes()
```

## Best Practices

1. **Always set Conventions** - Include `Conventions="CF-1.8"` in global attributes
2. **Use standard_name** - Follow CF standard name table
3. **Include units** - All coordinates and variables should have units
4. **Set axis attributes** - Use `set_axis_attributes()` for automatic setting
5. **Validate early** - Run `validate_cf()` before generating data
6. **Follow dimension order** - Use T, Z, Y, X ordering when possible
7. **Add long_name** - Provide human-readable descriptions

## CF Resources

- [CF Conventions](http://cfconventions.org/) - Official CF conventions documentation
- [CF Standard Names](http://cfconventions.org/standard-names.html) - Standard name table
- [CF Checker](https://github.com/cedadev/cf-checker) - External CF compliance checker

## Next Steps

- Learn about [History Tracking](history-tracking.md) to record dataset modifications
- See [Examples](../examples.md) for more CF compliance workflows
- Check the [API Reference](../api/dataset.md) for all CF-related methods
