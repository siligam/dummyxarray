# Examples

This page contains comprehensive examples demonstrating the features of Dummy Xarray.

## Basic Metadata-Only Dataset

Create a dataset specification without any data:

```python
from dummyxarray import DummyDataset

ds = DummyDataset()

# Set global attributes
ds.set_global_attrs(
    title="Test Climate Dataset",
    institution="DKRZ",
    experiment="historical",
    source="Example Model v1.0"
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

# Add coordinates (without data for now)
ds.add_coord("time", ["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

# Add variables (without data)
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    attrs={"long_name": "Near-Surface Air Temperature", "units": "K"}
)

# Export to YAML for documentation
print(ds.to_yaml())
ds.save_yaml("dataset_spec.yaml")
```

## Automatic Dimension Inference

Let dimensions be inferred from your data:

```python
import numpy as np
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.set_global_attrs(title="Auto-inferred Dataset")

# Create data with specific shape
temp_data = np.random.rand(12, 64, 128)

# Add variable with data - dimensions will be auto-inferred
ds.add_variable(
    "tas",
    data=temp_data,
    attrs={"units": "K", "long_name": "air_temperature"}
)

print("Dimensions were automatically inferred:")
print(ds.dims)  # {'dim_0': 12, 'dim_1': 64, 'dim_2': 128}
```

## With Encoding for Zarr/NetCDF

Specify encoding parameters for optimal storage:

```python
import numpy as np
from dummyxarray import DummyDataset

ds = DummyDataset()
ds.set_global_attrs(title="Dataset with Encoding")

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)

# Add coordinate with encoding
time_data = np.arange(12)
ds.add_coord(
    "time",
    ["time"],
    data=time_data,
    attrs={"units": "days since 2000-01-01"},
    encoding={"dtype": "int32"}
)

# Add variable with chunking and compression
temp_data = np.random.rand(12, 64, 128) * 20 + 273.15
ds.add_variable(
    "tas",
    ["time", "lat", "lon"],
    data=temp_data,
    attrs={"long_name": "Near-Surface Air Temperature", "units": "K"},
    encoding={
        "dtype": "float32",
        "chunks": (6, 32, 64),
        "compressor": None,  # Can use zarr.Blosc() or similar
    }
)

# Validate and write to Zarr
ds.validate()
ds.to_zarr("output.zarr")
```

## Loading and Modifying Specifications

Save and load dataset specifications:

```python
from dummyxarray import DummyDataset

# Create and save a specification
ds = DummyDataset()
ds.set_global_attrs(title="Template Dataset")
ds.add_dim("time", 12)
ds.add_variable("temperature", ["time"], attrs={"units": "K"})
ds.save_yaml("template.yaml")

# Load it later
loaded_ds = DummyDataset.load_yaml("template.yaml")

# Modify and use
loaded_ds.set_global_attrs(experiment="run_001")
print(loaded_ds.to_yaml())
```

## Validation Example

Catch errors early with validation:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)

# Add variable with correct shape
data = np.random.rand(10, 5)
ds.add_variable("test", dims=["time", "lat"], data=data)

# Validate - should pass
try:
    ds.validate()
    print("✓ Validation passed!")
except ValueError as e:
    print(f"✗ Validation failed: {e}")

# Try adding a variable with wrong dimension
ds2 = DummyDataset()
ds2.add_variable("bad_var", dims=["unknown_dim"])

try:
    ds2.validate()
except ValueError as e:
    print(f"✗ Caught error: {e}")
```

## Complete Workflow

A complete example from specification to xarray:

```python
import numpy as np
from dummyxarray import DummyDataset

# 1. Create specification
ds = DummyDataset()
ds.set_global_attrs(
    title="Complete Example",
    institution="Research Center",
    Conventions="CF-1.8"
)

# 2. Define structure
ds.add_dim("time", 365)
ds.add_dim("lat", 90)
ds.add_dim("lon", 180)

# 3. Add coordinates with data
time_data = np.arange(365)
lat_data = np.linspace(-90, 90, 90)
lon_data = np.linspace(-180, 180, 180)

ds.add_coord("time", ["time"], data=time_data, 
             attrs={"units": "days since 2020-01-01"})
ds.add_coord("lat", ["lat"], data=lat_data,
             attrs={"units": "degrees_north", "standard_name": "latitude"})
ds.add_coord("lon", ["lon"], data=lon_data,
             attrs={"units": "degrees_east", "standard_name": "longitude"})

# 4. Add variables with encoding
temp_data = np.random.rand(365, 90, 180) * 20 + 273.15
ds.add_variable(
    "temperature",
    ["time", "lat", "lon"],
    data=temp_data,
    attrs={
        "long_name": "Near-Surface Air Temperature",
        "units": "K",
        "standard_name": "air_temperature"
    },
    encoding={
        "dtype": "float32",
        "chunks": (30, 45, 90)
    }
)

# 5. Validate
ds.validate()

# 6. Convert to xarray
xr_ds = ds.to_xarray()
print(xr_ds)

# 7. Write to Zarr
ds.to_zarr("complete_example.zarr")
```

## Extract Metadata from Existing xarray Dataset

Create a template from an existing dataset:

```python
import xarray as xr
from dummyxarray import DummyDataset

# Load an existing xarray dataset
existing_ds = xr.open_dataset("my_data.nc")

# Extract metadata only (no data)
dummy_ds = DummyDataset.from_xarray(existing_ds, include_data=False)

# Save as a reusable template
dummy_ds.save_yaml("template.yaml")

# Or extract with data included
dummy_with_data = DummyDataset.from_xarray(existing_ds, include_data=True)
```

## Populate with Random Data for Testing

Generate meaningful random data based on metadata:

```python
from dummyxarray import DummyDataset

# Create structure without data
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 5)
ds.add_dim("lon", 8)

ds.add_coord("time", ["time"], attrs={"units": "days"})
ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

ds.add_variable("temperature", ["time", "lat", "lon"], 
                attrs={"units": "K", "standard_name": "air_temperature"})
ds.add_variable("precipitation", ["time", "lat", "lon"],
                attrs={"units": "kg m-2 s-1"})

# Populate all coordinates and variables with meaningful random data
ds.populate_with_random_data(seed=42)  # seed for reproducibility

# Check the generated data
print(f"Temperature range: {ds.variables['temperature'].data.min():.1f} - "
      f"{ds.variables['temperature'].data.max():.1f} K")
print(f"Latitude range: {ds.coords['lat'].data.min():.1f} - "
      f"{ds.coords['lat'].data.max():.1f}°")

# Convert to xarray and use for testing
xr_ds = ds.to_xarray()
```

## xarray-style Attribute Access

Access coordinates and variables using dot notation:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_coord("time", ["time"], attrs={"units": "days"})
ds.add_variable("temperature", ["time"], attrs={"units": "K"})

# Access using attribute notation (like xarray)
print(ds.time)                  # Access coordinate
print(ds.temperature)           # Access variable

# Modify via attribute access
ds.time.data = np.arange(10)

# Use assign_attrs for xarray-compatible API
ds.time.assign_attrs(standard_name="time", calendar="gregorian")

# Rich repr shows structure clearly
print(ds)
# Output shows:
# <dummyxarray.DummyDataset>
# Dimensions:
#   time: 10
# Coordinates:
#   ✓ time                 (time)               int64
# Data variables:
#   ✗ temperature          (time)               ?

# Inspect individual arrays
print(ds.time)
# Output:
# <dummyxarray.DummyArray>
# Dimensions: (time)
# Shape: (10,)
# dtype: int64
# Data: [0 1 2 3 4 5 6 7 8 9]
# Attributes:
#     units: days
#     standard_name: time
#     calendar: gregorian
```

## Multi-File Dataset Support

Work with multiple NetCDF files as a single dataset:

```python
from dummyxarray import DummyDataset

# Open multiple files as one dataset
ds = DummyDataset.open_mfdataset("data/*.nc", concat_dim="time")

# Frequency is automatically inferred
print(ds.coords['time'].attrs['frequency'])  # e.g., "1H" for hourly

# Group by time periods
decades = ds.groupby_time('10Y')

# Each decade is a separate DummyDataset
for i, decade in enumerate(decades):
    print(f"Decade {i}:")
    print(f"  Time steps: {decade.dims['time']}")
    print(f"  Time units: {decade.coords['time'].attrs['units']}")
    print(f"  Source files: {len(decade.get_source_files())}")

# Query which files contain specific time ranges
files = ds.get_source_files(time=slice(0, 100))
print(f"Files for first 100 timesteps: {files}")
```

## Intake Catalog Round-Trip

Complete round-trip workflow with Intake catalogs:

```python
from dummyxarray import DummyDataset
import tempfile
import yaml

# 1. Create original dataset
ds = DummyDataset()
ds.assign_attrs(
    title="Climate Model Output",
    institution="Example Climate Center",
    Conventions="CF-1.8"
)
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)
ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={"units": "K", "standard_name": "air_temperature"},
    encoding={"dtype": "float32", "chunks": [6, 32, 64]}
)

# 2. Export to Intake catalog
catalog_yaml = ds.to_intake_catalog(
    name="climate_data",
    description="Climate model output with temperature",
    driver="zarr",
    data_path="data/climate_model_output.zarr"
)

print("Generated Intake catalog:")
print(catalog_yaml)

# 3. Save to file
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    catalog_path = f.name
    ds.save_intake_catalog(catalog_path, name="climate_data")

# 4. Load from catalog (round-trip)
restored_ds = DummyDataset.from_intake_catalog(catalog_path, "climate_data")

# 5. Verify integrity
print(f"Original dims: {ds.dims}")
print(f"Restored dims: {restored_ds.dims}")
print(f"Dims match: {ds.dims == restored_ds.dims}")
print(f"Variables match: {set(ds.variables.keys()) == set(restored_ds.variables.keys())}")

# 6. Load from dictionary
catalog_dict = yaml.safe_load(catalog_yaml)
loaded_from_dict = DummyDataset.from_intake_catalog(catalog_dict, "climate_data")
print(f"Dict loading works: {loaded_from_dict.dims == ds.dims}")
```

## STAC Catalog Integration

### Basic STAC Item Creation

Create and export a dataset as a STAC Item:

```python
from dummyxarray import DummyDataset
import numpy as np

# Create dataset with spatial coordinates
ds = DummyDataset()
ds.add_dim('time', 12)
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

ds.add_coord('lat', ['lat'], data=np.linspace(-89.5, 89.5, 180))
ds.add_coord('lon', ['lon'], data=np.linspace(-179.5, 179.5, 360))

ds.add_variable('temperature', ['time', 'lat', 'lon'],
                attrs={'units': 'K', 'standard_name': 'air_temperature'})

# Add metadata
ds.attrs.update({
    'title': 'Global Temperature Data',
    'description': 'Monthly global temperature analysis',
    'time_coverage_start': '2020-01-01T00:00:00Z',
    'time_coverage_end': '2020-12-31T23:59:59Z'
})

# Convert to STAC Item
item = ds.to_stac_item(
    id='temperature-2020',
    properties={'model': 'ERA5', 'resolution': '1-degree'}
)

# Save to file
ds.save_stac_item('temperature_2020.json', id='temperature-2020')
print(f"STAC Item created: {item.id}")
print(f"Bbox: {item.bbox}")
```

### STAC Collection from Multiple Datasets

Create a collection from multiple related datasets:

```python
from dummyxarray import DummyDataset
import numpy as np

# Create multiple monthly datasets
datasets = []
for month in range(1, 13):
    ds = DummyDataset()
    ds.add_dim('lat', 180)
    ds.add_dim('lon', 360)
    
    ds.add_coord('lat', ['lat'], data=np.linspace(-89.5, 89.5, 180))
    ds.add_coord('lon', ['lon'], data=np.linspace(-179.5, 179.5, 360))
    
    ds.add_variable('sst', ['lat', 'lon'],
                    attrs={'units': 'degree_Celsius',
                           'standard_name': 'sea_surface_temperature'})
    
    ds.attrs.update({
        'title': f'SST 2020-{month:02d}',
        'time_coverage_start': f'2020-{month:02d}-01T00:00:00Z'
    })
    
    datasets.append(ds)

# Create collection
collection = DummyDataset.create_stac_collection(
    datasets,
    collection_id='sst-monthly-2020',
    description='Monthly sea surface temperature for 2020',
    license='CC-BY-4.0'
)

print(f"Collection created with {len(list(collection.get_items()))} items")
```

### Spatial Metadata Validation

Validate spatial metadata before creating STAC catalogs:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim('lat', 64)
ds.add_dim('lon', 128)

ds.add_coord('lat', ['lat'], 
             data=np.linspace(-45, 45, 64),
             attrs={'units': 'degrees_north', 'standard_name': 'latitude'})
ds.add_coord('lon', ['lon'],
             data=np.linspace(-90, 90, 128),
             attrs={'units': 'degrees_east', 'standard_name': 'longitude'})

# Validate spatial metadata
validation = ds.validate_spatial_metadata()

if validation['valid']:
    print("✓ Spatial metadata is valid")
    print(f"  Found: {', '.join(validation['found'])}")
    
    # Create STAC Item
    item = ds.to_stac_item(id='validated-dataset')
    print(f"  Bbox: {item.bbox}")
else:
    print("✗ Spatial validation failed:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

### Temporal Extent Inference

Automatically infer temporal extent from time coordinates:

```python
from dummyxarray import DummyDataset
import numpy as np

ds = DummyDataset()
ds.add_dim('time', 365)
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

# Add time coordinate with CF-compliant units
ds.add_coord('time', ['time'],
             data=np.arange(365),
             attrs={'units': 'days since 2020-01-01', 'calendar': 'gregorian'})

# Infer temporal extent
start, end = ds.infer_temporal_extent()

print(f"Temporal coverage: {start} to {end}")
print(f"Start: {ds.attrs['time_coverage_start']}")
print(f"End: {ds.attrs['time_coverage_end']}")

# Create STAC Item with inferred temporal extent
item = ds.to_stac_item(id='daily-data-2020')
print(f"STAC datetime: {item.datetime}")
```

### Regional Dataset with Custom Extent

Create a regional dataset with explicit spatial extent:

```python
from dummyxarray import DummyDataset
import numpy as np

# North America regional dataset
ds = DummyDataset()
ds.add_dim('lat', 100)
ds.add_dim('lon', 200)

ds.add_coord('lat', ['lat'], data=np.linspace(25, 70, 100))
ds.add_coord('lon', ['lon'], data=np.linspace(-170, -50, 200))

ds.add_variable('precipitation', ['lat', 'lon'],
                attrs={'units': 'mm/day', 'standard_name': 'precipitation_flux'})

# Add explicit spatial extent
ds.add_spatial_extent(
    lat_bounds=(25, 70),
    lon_bounds=(-170, -50)
)

ds.attrs.update({
    'title': 'North America Precipitation',
    'description': 'Regional precipitation data for North America',
    'region': 'North America'
})

# Create STAC Item
item = ds.to_stac_item(
    id='na-precipitation',
    properties={'region': 'north_america', 'coverage': 'regional'}
)

print(f"Regional bbox: {item.bbox}")
print(f"Spatial extent: {ds.attrs['geospatial_bounds']}")
```

### STAC Roundtrip (Save and Load)

Complete roundtrip workflow with STAC Items:

```python
from dummyxarray import DummyDataset
import numpy as np

# 1. Create original dataset
ds = DummyDataset()
ds.add_dim('time', 10)
ds.add_dim('lat', 64)
ds.add_dim('lon', 128)

ds.add_coord('lat', ['lat'], data=np.linspace(-45, 45, 64))
ds.add_coord('lon', ['lon'], data=np.linspace(-90, 90, 128))

ds.add_variable('temperature', ['time', 'lat', 'lon'],
                attrs={'units': 'K', 'standard_name': 'air_temperature'})

ds.attrs.update({
    'title': 'Temperature Analysis',
    'institution': 'Climate Research Center'
})

# 2. Save as STAC Item
ds.save_stac_item(
    'temperature_item.json',
    id='temp-analysis',
    properties={'version': '1.0', 'quality': 'validated'}
)

# 3. Load from STAC Item
loaded_ds = DummyDataset.load_stac_item('temperature_item.json')

# 4. Verify roundtrip
print(f"Original dims: {ds.dims}")
print(f"Loaded dims: {loaded_ds.dims}")
print(f"Dims match: {ds.dims == loaded_ds.dims}")
print(f"Variables match: {set(ds.variables.keys()) == set(loaded_ds.variables.keys())}")
print(f"Title preserved: {loaded_ds.attrs.get('title') == ds.attrs['title']}")
```

## More Examples

For more examples, check out the example files in the repository:

- `example.py` - Basic usage and core features
- `example_from_xarray.py` - Extracting metadata from xarray datasets
- `example_populate.py` - Data population with random data
- `example_mfdataset.py` - Multi-file dataset support (old version)
- `example_groupby_time.py` - Time-based grouping with 5 comprehensive examples
- `intake_catalog_example.py` - Complete Intake catalog round-trip demonstration
- Basic usage examples
- Automatic dimension inference
- Encoding specifications
- Validation demonstrations
- xarray conversion
- Zarr writing
- YAML save/load
- Intake catalog export and import
