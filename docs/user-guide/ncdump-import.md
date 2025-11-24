# Importing from ncdump Headers

dummyxarray can parse `ncdump -h` output to create dataset structures from existing NetCDF files.

## Overview

The `from_ncdump_header()` function parses the output of `ncdump -h` and creates a `DummyDataset`
with the same structure. This is useful for:

- **Replicating structures** - Copy metadata from existing datasets
- **Template creation** - Use real datasets as templates
- **Quick inspection** - Understand dataset structure without loading data
- **Documentation** - Extract and document dataset schemas

## Basic Usage

### Step 1: Get ncdump Header

```bash
# Generate header from NetCDF file
ncdump -h your_file.nc > header.txt
```

### Step 2: Import to DummyDataset

```python
from dummyxarray import from_ncdump_header

# Read the header file
with open('header.txt', 'r') as f:
    header_text = f.read()

# Create DummyDataset
ds = from_ncdump_header(header_text)

# The dataset now has the same structure
print(ds)
```

## What Gets Imported

The parser extracts:

- ✅ **Dimensions** - Including UNLIMITED dimensions
- ✅ **Variables** - With dimensions and data types
- ✅ **Coordinates** - Automatically detected
- ✅ **Attributes** - Variable and global attributes
- ✅ **Metadata** - All CF-compliant metadata

**Note**: Data arrays are NOT imported, only the structure and metadata.

## Complete Example

```python
from dummyxarray import from_ncdump_header

# Example ncdump output
header = """
netcdf climate_data {
dimensions:
    time = UNLIMITED ; // (365 currently)
    lat = 64 ;
    lon = 128 ;
variables:
    double time(time) ;
        time:units = "days since 2000-01-01" ;
        time:calendar = "gregorian" ;
        time:axis = "T" ;
    double lat(lat) ;
        lat:units = "degrees_north" ;
        lat:standard_name = "latitude" ;
        lat:axis = "Y" ;
    double lon(lon) ;
        lon:units = "degrees_east" ;
        lon:standard_name = "longitude" ;
        lon:axis = "X" ;
    float temperature(time, lat, lon) ;
        temperature:units = "K" ;
        temperature:standard_name = "air_temperature" ;
        temperature:long_name = "Air Temperature" ;

// global attributes:
        :Conventions = "CF-1.8" ;
        :title = "Climate Model Output" ;
}
"""

# Import structure
ds = from_ncdump_header(header)

# Check what was imported
print(f"Dimensions: {ds.dims}")
print(f"Coordinates: {list(ds.coords.keys())}")
print(f"Variables: {list(ds.variables.keys())}")
print(f"Global attrs: {ds.attrs}")
```

## Coordinate Detection

The parser automatically identifies coordinates using this rule:

**A variable is a coordinate if:**
- It has exactly one dimension
- The dimension name matches the variable name

```python
# These are detected as coordinates:
double time(time) ;      # ✓ Coordinate
double lat(lat) ;        # ✓ Coordinate
double lon(lon) ;        # ✓ Coordinate

# These are detected as variables:
float temperature(time, lat, lon) ;  # ✗ Variable (multi-dim)
float bounds(lat, nv) ;              # ✗ Variable (dims don't match name)
```

## Handling UNLIMITED Dimensions

UNLIMITED dimensions are handled automatically:

```python
# ncdump shows:
# time = UNLIMITED ; // (365 currently)

# Parser extracts the current size (365)
ds = from_ncdump_header(header)
print(ds.dims['time'])  # 365
```

If no current size is specified, the dimension size will be `None`:

```python
# time = UNLIMITED ;  (no current size)
# ds.dims['time'] will be None
```

## Working with Imported Datasets

Once imported, you can work with the dataset normally:

### Populate with Data

```python
# Add random data for testing
ds.populate_with_random_data(seed=42)

# Now convert to xarray
xr_ds = ds.to_xarray()
```

### Validate CF Compliance

```python
# Check CF compliance
result = ds.validate_cf()
print(f"Warnings: {len(result['warnings'])}")
```

### Modify Structure

```python
# Add new variables
ds.add_variable(
    "humidity",
    dims=["time", "lat", "lon"],
    attrs={"units": "%", "standard_name": "relative_humidity"}
)

# Update attributes
ds.assign_attrs(history="Modified with dummyxarray")
```

### Export as Template

```python
# Save as YAML template
ds.save_yaml("template.yaml")

# Later, load and reuse
ds2 = DummyDataset.load_yaml("template.yaml")
```

## History Tracking

By default, history is recorded when importing:

```python
ds = from_ncdump_header(header, record_history=True)

# View construction history
history = ds.get_history()
print(f"Operations: {len(history)}")

# Export as Python code
python_code = ds.export_history('python')
print(python_code)
```

Disable history if not needed:

```python
ds = from_ncdump_header(header, record_history=False)
```

## Supported Features

### Dimensions
- ✅ Fixed-size dimensions
- ✅ UNLIMITED dimensions with current size
- ✅ UNLIMITED dimensions without size (→ None)

### Variables
- ✅ All NetCDF data types (double, float, int, etc.)
- ✅ Multi-dimensional variables
- ✅ Coordinate variables
- ✅ Variable attributes

### Attributes
- ✅ String attributes
- ✅ Numeric attributes (int, float)
- ✅ Array attributes
- ✅ Global attributes

### Not Supported
- ❌ Data arrays (only structure)
- ❌ Groups (NetCDF-4 feature)
- ❌ User-defined types
- ❌ Compound types

## Practical Workflows

### Workflow 1: Replicate Existing Dataset

```python
# Get structure from existing file
!ncdump -h existing_data.nc > structure.txt

# Import structure
with open('structure.txt') as f:
    ds = from_ncdump_header(f.read())

# Populate with new data
ds.populate_with_random_data()

# Save as new file
ds.to_zarr("new_data.zarr")
```

### Workflow 2: Document Dataset Schema

```python
# Import structure
ds = from_ncdump_header(header_text)

# Export as YAML documentation
ds.save_yaml("dataset_schema.yaml")

# Export history as Python script
with open('create_dataset.py', 'w') as f:
    f.write(ds.export_history('python'))
```

### Workflow 3: Validate and Fix Metadata

```python
# Import existing structure
ds = from_ncdump_header(header_text)

# Check CF compliance
result = ds.validate_cf()

# Fix issues
ds.infer_axis()
ds.set_axis_attributes()

# Re-validate
result = ds.validate_cf()
print(f"Warnings: {len(result['warnings'])}")
```

## Tips and Best Practices

1. **Always validate** - Run `validate_cf()` after importing
2. **Check coordinates** - Verify coordinate detection is correct
3. **Handle UNLIMITED** - Be aware of None dimension sizes
4. **Add encoding** - Set chunks and compression for new data
5. **Document changes** - Use history tracking for reproducibility

## Limitations

- Only parses metadata, not data
- Assumes standard ncdump format
- May not handle all edge cases
- Groups and complex types not supported

## See Also

- [CF Compliance](cf-compliance.md) - Validate imported datasets
- [History Tracking](history-tracking.md) - Track modifications
- [YAML Export](yaml-export.md) - Save as templates
- [Examples](../examples.md) - More ncdump import examples
