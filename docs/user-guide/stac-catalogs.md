# STAC Catalogs

## Overview

DummyXarray provides comprehensive support for **STAC (SpatioTemporal Asset Catalog)**, a standardized way to describe geospatial assets. STAC support enables you to:

- Export datasets as STAC Items and Collections
- Import datasets from STAC catalogs
- Validate spatial and temporal metadata
- Integrate with the broader STAC ecosystem

## Installation

STAC support requires optional dependencies:

```bash
pip install dummyxarray[stac]
```

This installs:
- `pystac` - Core STAC library
- `python-dateutil` - Date parsing utilities

## Core Concepts

### STAC Items

A **STAC Item** represents a single spatiotemporal asset (e.g., a dataset for a specific time and location).

### STAC Collections

A **STAC Collection** groups multiple related STAC Items together with shared metadata.

## Basic Usage

### Creating STAC Items

Convert a dataset to a STAC Item:

```python
from dummyxarray import DummyDataset
import numpy as np

# Create a dataset with spatial coordinates
ds = DummyDataset()
ds.add_dim('time', 10)
ds.add_dim('lat', 64)
ds.add_dim('lon', 128)

ds.add_coord('lat', ['lat'], data=np.linspace(-45, 45, 64))
ds.add_coord('lon', ['lon'], data=np.linspace(-90, 90, 128))

ds.add_variable('temperature', ['time', 'lat', 'lon'], 
                attrs={'units': 'K', 'long_name': 'Air Temperature'})

# Add metadata
ds.attrs.update({
    'title': 'Climate Model Output',
    'description': 'Temperature data from climate simulation',
    'time_coverage_start': '2020-01-01T00:00:00Z',
    'time_coverage_end': '2020-12-31T23:59:59Z'
})

# Convert to STAC Item
item = ds.to_stac_item(
    id='climate-2020',
    geometry={
        'type': 'Polygon',
        'coordinates': [[
            [-90, -45], [90, -45], [90, 45], [-90, 45], [-90, -45]
        ]]
    }
)

print(f"STAC Item ID: {item.id}")
print(f"Geometry: {item.geometry['type']}")
print(f"Properties: {list(item.properties.keys())}")
```

### Loading from STAC Items

Import a dataset from a STAC Item:

```python
# Load from STAC Item
loaded_ds = DummyDataset.from_stac_item(item)

print(f"Dimensions: {loaded_ds.dims}")
print(f"Variables: {list(loaded_ds.variables.keys())}")
print(f"Title: {loaded_ds.attrs['title']}")
```

### Creating STAC Collections

Convert a dataset to a STAC Collection:

```python
# Create a collection
collection = ds.to_stac_collection(
    id='climate-collection',
    description='Climate model output collection',
    license='CC-BY-4.0'
)

print(f"Collection ID: {collection.id}")
print(f"Description: {collection.description}")
print(f"Number of items: {len(list(collection.get_items()))}")
```

### Multi-Asset Collections

Create a collection from multiple datasets:

```python
# Create multiple datasets
temperature_ds = DummyDataset()
temperature_ds.attrs['title'] = 'Temperature Data'
# ... configure temperature_ds ...

precipitation_ds = DummyDataset()
precipitation_ds.attrs['title'] = 'Precipitation Data'
# ... configure precipitation_ds ...

wind_ds = DummyDataset()
wind_ds.attrs['title'] = 'Wind Data'
# ... configure wind_ds ...

# Create collection from multiple datasets
collection = DummyDataset.create_stac_collection(
    [temperature_ds, precipitation_ds, wind_ds],
    collection_id='climate-2020',
    description='Complete climate dataset for 2020',
    license='CC-BY-4.0'
)

print(f"Collection contains {len(list(collection.get_items()))} items")
```

## File I/O

### Saving STAC Items

Save a STAC Item to a JSON file:

```python
# Save to file
ds.save_stac_item(
    'climate_item.json',
    id='climate-2020',
    geometry={
        'type': 'Polygon',
        'coordinates': [[[-90, -45], [90, -45], [90, 45], [-90, 45], [-90, -45]]]
    }
)

# Load from file
loaded_ds = DummyDataset.load_stac_item('climate_item.json')
```

### Saving STAC Collections

Save a STAC Collection to a JSON file:

```python
# Save collection
ds.save_stac_collection(
    'climate_collection.json',
    id='climate-collection',
    description='Climate model output'
)

# Load collection
loaded_ds = DummyDataset.load_stac_collection('climate_collection.json')
```

## Spatial Metadata

### Adding Spatial Extent

Explicitly add spatial extent information:

```python
ds = DummyDataset()

# Add spatial extent
ds.add_spatial_extent(
    lat_bounds=(-60, 85),
    lon_bounds=(-180, 180)
)

print(f"Spatial bounds: {ds.attrs['geospatial_bounds']}")
```

### Automatic Bbox Extraction

DummyXarray automatically extracts bounding boxes from:

1. **`geospatial_bounds` attribute** (highest priority)
2. **Lat/lon coordinates** (fallback)

```python
ds = DummyDataset()
ds.add_dim('lat', 64)
ds.add_dim('lon', 128)

# Bbox will be automatically extracted from these coordinates
ds.add_coord('lat', ['lat'], data=np.linspace(-45, 45, 64))
ds.add_coord('lon', ['lon'], data=np.linspace(-90, 90, 128))

item = ds.to_stac_item(id='auto-bbox')
print(f"Automatic bbox: {item.bbox}")  # [-90, -45, 90, 45]
```

### Validating Spatial Metadata

Validate spatial metadata before creating STAC Items:

```python
# Validate spatial metadata
validation = ds.validate_spatial_metadata()

if validation['valid']:
    print("✓ Spatial metadata is valid")
else:
    print("✗ Spatial metadata issues:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

## Temporal Metadata

### Inferring Temporal Extent

Automatically infer temporal extent from time coordinates:

```python
ds = DummyDataset()
ds.add_dim('time', 365)

# Add time coordinate with units
ds.add_coord('time', ['time'], 
             data=np.arange(365),
             attrs={'units': 'days since 2020-01-01'})

# Infer temporal extent
start, end = ds.infer_temporal_extent()

print(f"Start: {start}")  # 2020-01-01
print(f"End: {end}")      # 2020-12-31
print(f"Coverage start: {ds.attrs['time_coverage_start']}")
print(f"Coverage end: {ds.attrs['time_coverage_end']}")
```

## Integration with Intake Catalogs

STAC and Intake catalogs can be used together:

```python
# Save both catalog types
ds.save_intake_catalog('catalog.yaml', name='climate-data')
ds.save_stac_item('catalog.json', id='climate-data')

# Load from either format
intake_ds = DummyDataset.from_intake_catalog('catalog.yaml', 'climate-data')
stac_ds = DummyDataset.load_stac_item('catalog.json')
```

## Advanced Features

### Custom Properties

Add custom properties to STAC Items:

```python
item = ds.to_stac_item(
    id='climate-2020',
    properties={
        'model': 'CESM2',
        'scenario': 'SSP2-4.5',
        'institution': 'NCAR',
        'processing_level': 'L3'
    }
)

print(f"Model: {item.properties['model']}")
```

### Geometry from Attributes

Use geometry from dataset attributes:

```python
ds.attrs['geospatial_bounds'] = {
    'type': 'Polygon',
    'coordinates': [[
        [-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]
    ]]
}

# Geometry will be extracted automatically
item = ds.to_stac_item(id='global-coverage')
print(f"Geometry type: {item.geometry['type']}")
```

### Collection Metadata

Collections preserve dataset metadata:

```python
collection = ds.to_stac_collection(
    id='climate-collection',
    description='Climate model output'
)

# Access collection metadata
print(f"Dimensions: {collection.extra_fields.get('dims')}")
print(f"Variables: {collection.extra_fields.get('variables')}")
```

## Best Practices

### 1. Always Include Spatial Information

```python
# Good: Explicit spatial extent
ds.add_spatial_extent(lat_bounds=(-90, 90), lon_bounds=(-180, 180))

# Also good: Spatial coordinates
ds.add_coord('lat', ['lat'], data=np.linspace(-90, 90, 180))
ds.add_coord('lon', ['lon'], data=np.linspace(-180, 180, 360))
```

### 2. Use Descriptive IDs

```python
# Good: Descriptive, unique IDs
item = ds.to_stac_item(id='temperature-2020-01-global-daily')

# Avoid: Generic IDs
item = ds.to_stac_item(id='item1')  # Not descriptive
```

### 3. Include Temporal Information

```python
ds.attrs.update({
    'time_coverage_start': '2020-01-01T00:00:00Z',
    'time_coverage_end': '2020-12-31T23:59:59Z'
})
```

### 4. Validate Before Export

```python
# Validate spatial metadata
validation = ds.validate_spatial_metadata()
if not validation['valid']:
    print("Fix these issues before creating STAC Item:")
    for issue in validation['issues']:
        print(f"  - {issue}")
else:
    item = ds.to_stac_item(id='validated-item')
```

### 5. Use Appropriate Licenses

```python
collection = ds.to_stac_collection(
    id='open-data',
    license='CC-BY-4.0'  # Use standard license identifiers
)
```

## Error Handling

### Missing Spatial Data

```python
ds = DummyDataset()  # No spatial coordinates

try:
    item = ds.to_stac_item(id='no-spatial')
    # Item will be created, but bbox will be None
    print(f"Bbox: {item.bbox}")  # None
except Exception as e:
    print(f"Error: {e}")
```

### Invalid Geometry

```python
# Validate before creating
validation = ds.validate_spatial_metadata()
if validation['valid']:
    item = ds.to_stac_item(id='valid-item')
```

### Collection with No Items

```python
try:
    # This will raise an error
    collection = DummyDataset.create_stac_collection(
        [],  # Empty list
        collection_id='empty'
    )
except Exception as e:
    print(f"Error: {e}")  # "At least one dataset is required"
```

## Complete Example

Here's a complete workflow from dataset creation to STAC export:

```python
from dummyxarray import DummyDataset
import numpy as np

# 1. Create dataset with spatial/temporal coordinates
ds = DummyDataset()
ds.add_dim('time', 12)
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

ds.add_coord('time', ['time'], 
             data=np.arange(12),
             attrs={'units': 'months since 2020-01-01'})
ds.add_coord('lat', ['lat'], data=np.linspace(-90, 90, 180))
ds.add_coord('lon', ['lon'], data=np.linspace(-180, 180, 360))

# 2. Add variables
ds.add_variable('temperature', ['time', 'lat', 'lon'],
                attrs={'units': 'K', 'standard_name': 'air_temperature'})
ds.add_variable('precipitation', ['time', 'lat', 'lon'],
                attrs={'units': 'mm/day', 'standard_name': 'precipitation_flux'})

# 3. Add global metadata
ds.attrs.update({
    'title': 'Global Climate Data 2020',
    'description': 'Monthly global temperature and precipitation',
    'institution': 'Climate Research Center',
    'source': 'Climate Model v2.0'
})

# 4. Infer temporal extent
start, end = ds.infer_temporal_extent()
print(f"Temporal coverage: {start} to {end}")

# 5. Validate spatial metadata
validation = ds.validate_spatial_metadata()
print(f"Spatial validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")

# 6. Create and save STAC Item
ds.save_stac_item(
    'climate_2020.json',
    id='global-climate-2020',
    properties={
        'model': 'ClimateModel-v2',
        'resolution': '1-degree'
    }
)

# 7. Create and save STAC Collection
ds.save_stac_collection(
    'climate_collection.json',
    id='climate-monthly',
    description='Monthly global climate data',
    license='CC-BY-4.0'
)

print("✓ STAC catalogs created successfully!")
```

## See Also

- [Spatial Metadata Guide](spatial-metadata.md) - Detailed spatial metadata handling
- [Geospatial Workflows](geospatial-workflows.md) - End-to-end geospatial examples
- [Intake Catalogs](intake-catalogs.md) - Alternative catalog format
- [CF Compliance](cf-compliance.md) - CF conventions for geospatial data
