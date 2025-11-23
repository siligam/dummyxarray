# Dummy Xarray

A lightweight xarray-like object for building dataset metadata specifications before creating actual xarray datasets.

## Features

✅ **Define dimensions and their sizes**  
✅ **Add variables and coordinates with metadata**  
✅ **Automatic dimension inference from data**  
✅ **xarray-style attribute access** (`ds.time`, `ds.temperature`)  
✅ **Rich repr for interactive exploration** (DummyDataset and DummyArray)  
✅ **Populate with random but meaningful data** (for testing)  
✅ **Create from existing xarray.Dataset** (extract metadata)  
✅ **Create from YAML specifications**  
✅ **Export to YAML/JSON for documentation**  
✅ **Save/load specifications from YAML files**  
✅ **Support for encoding** (dtype, chunks, compression)  
✅ **Dataset validation** (dimension checks, shape matching)  
✅ **Convert to real xarray.Dataset**  
✅ **Write directly to Zarr format**

## Installation

### Using Pixi (Recommended)

```bash
# Install dependencies
pixi install

# Run tests
pixi run test

# Run examples
pixi run example
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Create a Dataset with Metadata

```python
from dummy_xarray import DummyDataset

ds = DummyDataset()

# Set global attributes (xarray-compatible API)
ds.assign_attrs(
    title="Climate Model Output",
    institution="DKRZ",
    experiment="historical"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

# Add coordinates
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

# Add variables
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    attrs={"long_name": "Near-Surface Air Temperature", "units": "K"}
)

# Export to YAML
print(ds.to_yaml())
```

### 2. Automatic Dimension Inference

```python
import numpy as np

ds = DummyDataset()

# Provide data - dimensions are inferred automatically
temp_data = np.random.rand(12, 64, 128)

ds.add_variable(
    "tas",
    data=temp_data,
    attrs={"units": "K", "long_name": "air_temperature"}
)

# Dimensions dim_0, dim_1, dim_2 are automatically created
print(ds.dims)  # {'dim_0': 12, 'dim_1': 64, 'dim_2': 128}
```

### 3. Add Encoding for Zarr/NetCDF

```python
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    data=temp_data,
    attrs={"long_name": "Temperature", "units": "K"},
    encoding={
        "dtype": "float32",
        "chunks": (6, 32, 64),
        "compressor": None,  # Can use zarr.Blosc() or similar
    }
)
```

### 4. Validate Dataset

```python
# Check for dimension mismatches, unknown dimensions, etc.
ds.validate()
```

### 5. Convert to xarray.Dataset

```python
# Once you have data in all variables/coordinates
xr_ds = ds.to_xarray()
print(xr_ds)
```

### 6. Write to Zarr

```python
# Write directly to Zarr format with encoding applied
ds.to_zarr("output.zarr")
```

### 7. Create from Existing xarray.Dataset

```python
import xarray as xr

# Extract metadata from an existing xarray dataset
existing_ds = xr.open_dataset("my_data.nc")
dummy_ds = DummyDataset.from_xarray(existing_ds, include_data=False)

# Save as template
dummy_ds.save_yaml("template.yaml")
```

### 8. Populate with Random Data

```python
# Create structure without data
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_variable("temperature", ["time", "lat"], 
                attrs={"units": "K", "standard_name": "air_temperature"})

# Populate with meaningful random data
ds.populate_with_random_data(seed=42)

# Now has realistic data: temperature in Kelvin, lat from -90 to 90
print(ds.variables["temperature"].data.mean())  # ~280 K
```

### 9. xarray-style Attribute Access

```python
# Access coordinates and variables as attributes (like xarray)
ds.time                    # Same as ds.coords['time']
ds.temperature             # Same as ds.variables['temperature']

# Modify via attribute access
ds.time.data = np.arange(10)
ds.time.assign_attrs(standard_name="time", calendar="gregorian")

# Or use dictionary-style access
ds.temperature.attrs["cell_methods"] = "time: mean"

# Inspect with rich repr
print(ds.time)             # Shows dimensions, shape, dtype, data, attrs
```

### 10. Save/Load Specifications

```python
# Save the dataset structure to YAML
ds.save_yaml("dataset_spec.yaml")

# Load it back later
loaded_ds = DummyDataset.load_yaml("dataset_spec.yaml")
```

## Example Output (YAML)

```yaml
dimensions:
  time: 12
  lat: 180
  lon: 360
coordinates:
  lat:
    dims:
    - lat
    attrs:
      units: degrees_north
    has_data: false
  lon:
    dims:
    - lon
    attrs:
      units: degrees_east
    has_data: false
variables:
  tas:
    dims:
    - time
    - lat
    - lon
    attrs:
      long_name: Near-Surface Air Temperature
      units: K
    encoding:
      dtype: float32
      chunks: [6, 32, 64]
    has_data: true
attrs:
  title: Climate Model Output
  institution: DKRZ
  experiment: historical
```

## Running Examples

```bash
pixi run example
```

This will run through all the example use cases including:
- Basic metadata-only dataset creation
- Automatic dimension inference
- Encoding specifications
- Validation
- Conversion to xarray
- Writing to Zarr
- Loading from YAML

## Development

### Code Quality Tools

The project uses pixi for managing development tasks:

```bash
# Format code (applies black and isort)
pixi run format

# Check formatting without modifying files
pixi run check-format

# Run linters (flake8 for Python, markdownlint for Markdown)
pixi run lint

# Run all checks (format check + lint)
pixi run check

# Run tests
pixi run test
```

### Individual Tools

```bash
# Format Python code with black
pixi run format-python

# Sort imports with isort
pixi run format-imports

# Lint Python code with flake8
pixi run lint-python

# Lint Markdown files
pixi run lint-markdown
```

### Configuration Files

- `.flake8` - Flake8 linting configuration
- `pyproject.toml` - Black and isort configuration
- `.markdownlint-cli2.yaml` - Markdown linting rules

## Use Cases

### 1. **Dataset Planning**
Define your dataset structure before generating data. Export to YAML for documentation and review.

### 2. **Template Generation**
Create reusable dataset templates that can be loaded and populated with data later.

### 3. **CF-Compliance Preparation**
Set up all required metadata (units, long_name, standard_name) before creating the actual dataset.

### 4. **Zarr Workflow**
Define chunking and compression strategies, then write directly to Zarr with optimal settings.

### 5. **Metadata Validation**
Catch dimension mismatches and missing coordinates early, before expensive data operations.

## API Reference

### DummyDataset

**Methods:**
- `assign_attrs(**kwargs)` - Set global attributes (xarray-compatible, returns self)
- `set_global_attrs(**kwargs)` - Set global dataset attributes (legacy)
- `add_dim(name, size)` - Add a dimension
- `add_coord(name, dims, attrs, data, encoding)` - Add a coordinate variable
- `add_variable(name, dims, attrs, data, encoding)` - Add a data variable
- `populate_with_random_data(seed=None)` - Fill with meaningful random data
- `validate(strict_coords=False)` - Validate dataset structure
- `to_dict()` - Export to dictionary
- `to_json(**kwargs)` - Export to JSON string
- `to_yaml()` - Export to YAML string
- `save_yaml(path)` - Save specification to YAML file
- `load_yaml(path)` - Load specification from YAML file (class method)
- `from_xarray(xr_ds, include_data=True)` - Create from xarray.Dataset (class method)
- `to_xarray(validate=True)` - Convert to xarray.Dataset
- `to_zarr(store_path, mode='w', validate=True)` - Write to Zarr format

### DummyArray

Represents a single variable or coordinate with:
- `dims` - List of dimension names
- `attrs` - Metadata dictionary
- `data` - Optional numpy array
- `encoding` - Encoding parameters (dtype, chunks, compressor, etc.)

**Methods:**
- `assign_attrs(**kwargs)` - Set attributes (xarray-compatible, returns self)
- `infer_dims_from_data()` - Infer dimension names from data shape
- `to_dict()` - Export to dictionary

## Future Extensions

Possible enhancements:
- CF metadata helpers (standard_name, axis, bounds detection)
- CMIP6 table-driven variable templates
- Automatic bounds generation (lat_bnds, time_bnds)
- Dimension registry with axis labels (X/Y/Z/T)
- Plugin system for custom validators

## License

This is a demonstration/utility tool. Feel free to use and modify as needed.
