# CF Standards with cf_xarray

dummyxarray uses `cf_xarray` to apply community-agreed CF standards to your datasets.

## Overview

dummyxarray integrates `cf_xarray` to provide:

- **Community standards** - Based on official CF conventions
- **Automatic detection** - Uses criteria from MetPy and Iris
- **Ecosystem integration** - Consistent with xarray tools
- **Comprehensive validation** - Beyond basic checks

## Why cf_xarray?

Instead of creating our own interpretation of CF standards, we use `cf_xarray`
which implements community-agreed criteria for:

- Axis detection (X, Y, Z, T)
- Coordinate identification
- Attribute requirements
- Standard names

This ensures your datasets are compatible with the broader scientific Python ecosystem.

## Installation

cf_xarray is automatically installed as a dependency when you install dummyxarray:

```bash
pip install dummyxarray
# or
pixi install
```

## Basic Usage

### Apply CF Standards

```python
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.add_dim("time", 12)
ds.add_coord(
    "time",
    dims=["time"],
    attrs={"units": "days since 2000-01-01"}
)

# Apply CF standards using cf_xarray (no data needed!)
result = ds.apply_cf_standards()

# Check what was detected
print(result['axes_detected'])  # {'time': 'T'}
print(result['attrs_added'])    # {'time': {'axis': 'T', ...}}

# Coordinate now has proper CF attributes
print(ds.coords['time'].attrs)
# {'units': 'days since 2000-01-01', 'axis': 'T', 'standard_name': 'time'}
```

### Validate CF Metadata

```python
# Validate against CF standards (no data needed!)
result = ds.validate_cf_metadata()

print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print(f"Warnings: {result['warnings']}")
print(f"Suggestions: {result['suggestions']}")
```

## Works Without Data! 🎉

**Great news**: Both `apply_cf_standards()` and `validate_cf_metadata()` now work
**without requiring data to be populated**!

### How?

The functions automatically create temporary dummy arrays (zeros) just for cf_xarray
processing, then discard them - keeping only the detected metadata. Your actual
dataset remains metadata-only.

```python
# Works perfectly without data!
ds = DummyDataset()
ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_variable("temperature", dims=["time"], attrs={"units": "K"})

# No data needed - metadata-only!
result = ds.apply_cf_standards()
print(result['axes_detected'])  # {'time': 'T'}

# Data is still None
print(ds.coords['time'].data)  # None
```

### Optional: Use Real Data

If you already have data or want to populate it, that works too:

```python
# Optional: populate with data
ds.populate_with_random_data(seed=42)

# Works the same way
ds.apply_cf_standards()
```

## Complete Example

```python
from dummyxarray import DummyDataset

# Create dataset with minimal metadata
ds = DummyDataset()
ds.assign_attrs(Conventions="CF-1.8", title="Climate Data")

# Add coordinates with basic attributes
ds.add_dim("time", 365)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

ds.add_coord("time", dims=["time"], 
             attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", dims=["lat"], 
             attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], 
             attrs={"units": "degrees_east"})

ds.add_variable("temperature", dims=["time", "lat", "lon"],
                attrs={"standard_name": "air_temperature", "units": "K"})

# Apply CF standards
if ds.check_cf_standards_available():
    result = ds.apply_cf_standards()
    print(f"Detected axes: {result['axes_detected']}")
    # Output: {'time': 'T', 'lat': 'Y', 'lon': 'X'}
    
    # Validate
    validation = ds.validate_cf_metadata()
    if validation['valid']:
        print("✓ CF compliant!")
else:
    print("Install cf_xarray for CF standards support")
```

## What Gets Added

cf_xarray automatically adds appropriate attributes based on detection:

### Time Coordinates
```python
# Before
attrs = {"units": "days since 2000-01-01"}

# After apply_cf_standards()
attrs = {
    "units": "days since 2000-01-01",
    "axis": "T",
    "standard_name": "time"
}
```

### Latitude Coordinates
```python
# Before
attrs = {"units": "degrees_north"}

# After
attrs = {
    "units": "degrees_north",
    "axis": "Y",
    "standard_name": "latitude"
}
```

### Longitude Coordinates
```python
# Before
attrs = {"units": "degrees_east"}

# After
attrs = {
    "units": "degrees_east",
    "axis": "X",
    "standard_name": "longitude"
}
```

### Vertical Coordinates
```python
# Before
attrs = {"units": "hPa", "positive": "down"}

# After
attrs = {
    "units": "hPa",
    "positive": "down",
    "axis": "Z",
    "standard_name": "air_pressure"
}
```

## Detection Criteria

cf_xarray uses sophisticated criteria to detect coordinates:

### By Units
- `degrees_north`, `degree_north`, `degrees_N` → Latitude (Y)
- `degrees_east`, `degree_east`, `degrees_E` → Longitude (X)
- Time units like `days since YYYY-MM-DD` → Time (T)
- Pressure units like `hPa`, `Pa`, `mbar` → Vertical (Z)

### By Standard Name
- `latitude`, `grid_latitude` → Y axis
- `longitude`, `grid_longitude` → X axis
- `time` → T axis
- `air_pressure`, `altitude`, `height` → Z axis

### By Axis Attribute
- `axis="X"` → X axis
- `axis="Y"` → Y axis
- `axis="Z"` → Z axis
- `axis="T"` → T axis

### By Name Pattern
- Names like `lat`, `latitude`, `y` → Y axis
- Names like `lon`, `longitude`, `x` → X axis
- Names like `time`, `t` → T axis
- Names like `lev`, `level`, `z`, `height` → Z axis

## Built-in vs cf_xarray

| Feature | Built-in | cf_xarray |
|---------|----------|-----------|
| **Dependencies** | None | cf_xarray |
| **Speed** | Fast | Moderate |
| **Standards** | Basic | Community-agreed |
| **Detection** | Simple patterns | Comprehensive criteria |
| **Validation** | Essential checks | Thorough |
| **Ecosystem** | Standalone | xarray-compatible |

### When to Use Built-in

- Quick prototyping
- No external dependencies needed
- Simple datasets
- Fast iteration

### When to Use cf_xarray

- Production datasets
- Publishing data
- Ecosystem compatibility
- Comprehensive validation
- Following community standards

## Workflow Recommendations

### Development Workflow

```python
# During development: use built-in for speed
ds.infer_axis()
ds.set_axis_attributes()
result = ds.validate_cf()
```

### Production Workflow

```python
# For production: use cf_xarray for standards
if ds.check_cf_standards_available():
    ds.apply_cf_standards()
    result = ds.validate_cf_metadata(strict=True)
    
    if not result['valid']:
        print("Fix these issues:")
        for error in result['errors']:
            print(f"  - {error}")
else:
    # Fallback to built-in
    ds.infer_axis()
    ds.set_axis_attributes()
```

## Advanced Usage

### Verbose Mode

```python
# See what cf_xarray is doing
result = ds.apply_cf_standards(verbose=True)
```

### Strict Validation

```python
# Treat warnings as errors
result = ds.validate_cf_metadata(strict=True)
```

### Check Availability

```python
# Check before using
if ds.check_cf_standards_available():
    ds.apply_cf_standards()
else:
    print("Install: pip install cf_xarray")
```

## Integration with Other Tools

cf_xarray makes your datasets compatible with:

- **xarray** - Native integration
- **MetPy** - Meteorological calculations
- **Iris** - Climate data analysis
- **Cartopy** - Map projections
- **Dask** - Parallel computing

## Troubleshooting

### cf_xarray Not Available

```python
# Check if installed
import importlib.util
if importlib.util.find_spec("cf_xarray") is None:
    print("Install: pip install cf_xarray")
```

### Attributes Not Detected

If cf_xarray doesn't detect your coordinates:

1. Check units are CF-compliant
2. Add `standard_name` attribute
3. Use recognized coordinate names
4. Add `axis` attribute explicitly

### Validation Warnings

Common warnings and fixes:

```python
# Warning: Missing standard_name
ds.coords['time'].attrs['standard_name'] = 'time'

# Warning: Missing axis
ds.coords['lat'].attrs['axis'] = 'Y'

# Warning: Non-standard units
ds.coords['lat'].attrs['units'] = 'degrees_north'  # Not 'deg N'
```

## Best Practices

1. **Start minimal** - Add basic attributes, let cf_xarray fill the rest
2. **Use standard names** - Follow CF standard name table
3. **Validate early** - Check compliance during development
4. **Document choices** - Use history tracking for decisions
5. **Test compatibility** - Verify with xarray and other tools

## Resources

- [cf_xarray Documentation](https://cf-xarray.readthedocs.io/)
- [CF Conventions](http://cfconventions.org/)
- [CF Standard Names](http://cfconventions.org/standard-names.html)
- [MetPy Documentation](https://unidata.github.io/MetPy/)

## See Also

- [CF Compliance](cf-compliance.md) - Built-in CF features
- [Validation](validation.md) - Dataset validation
- [Examples](../examples.md) - More CF standards examples
