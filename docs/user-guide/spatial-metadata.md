# Spatial Metadata

## Overview

DummyXarray provides comprehensive support for spatial metadata, enabling you to describe the geographic extent and coordinate systems of your datasets. This is essential for geospatial data workflows and STAC catalog integration.

## Spatial Extent

### Adding Spatial Extent

Define the geographic boundaries of your dataset:

```python
from dummyxarray import DummyDataset

ds = DummyDataset()

# Add spatial extent
ds.add_spatial_extent(
    lat_bounds=(-90, 90),    # Latitude range
    lon_bounds=(-180, 180)   # Longitude range
)

# Check the added metadata
print(ds.attrs['geospatial_bounds'])
print(ds.attrs['geospatial_lat_min'])  # -90
print(ds.attrs['geospatial_lat_max'])  # 90
print(ds.attrs['geospatial_lon_min'])  # -180
print(ds.attrs['geospatial_lon_max'])  # 180
```

### Geospatial Bounds Format

The `geospatial_bounds` attribute uses GeoJSON format:

```python
ds.attrs['geospatial_bounds'] = {
    'type': 'Polygon',
    'coordinates': [[
        [-180, -90],  # Southwest corner
        [180, -90],   # Southeast corner
        [180, 90],    # Northeast corner
        [-180, 90],   # Northwest corner
        [-180, -90]   # Close the polygon
    ]]
}
```

## Coordinate Systems

### Adding Spatial Coordinates

Define latitude and longitude coordinates:

```python
import numpy as np

ds = DummyDataset()
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

# Add latitude coordinate
ds.add_coord('lat', ['lat'], 
             data=np.linspace(-90, 90, 180),
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude',
                 'long_name': 'Latitude'
             })

# Add longitude coordinate
ds.add_coord('lon', ['lon'],
             data=np.linspace(-180, 180, 360),
             attrs={
                 'units': 'degrees_east',
                 'standard_name': 'longitude',
                 'long_name': 'Longitude'
             })
```

### Alternative Coordinate Names

DummyXarray recognizes various coordinate naming conventions:

```python
# Standard names
ds.add_coord('lat', ['lat'], data=lat_data)
ds.add_coord('lon', ['lon'], data=lon_data)

# Alternative names (also recognized)
ds.add_coord('latitude', ['latitude'], data=lat_data)
ds.add_coord('longitude', ['longitude'], data=lon_data)

# CF-compliant identification via standard_name
ds.add_coord('y', ['y'], 
             data=lat_data,
             attrs={'standard_name': 'latitude'})
ds.add_coord('x', ['x'],
             data=lon_data,
             attrs={'standard_name': 'longitude'})
```

## Bounding Box Extraction

### Automatic Bbox Extraction

DummyXarray automatically extracts bounding boxes with a priority system:

1. **`geospatial_bounds` attribute** (highest priority)
2. **Lat/lon coordinates** (automatic fallback)

```python
import numpy as np

ds = DummyDataset()
ds.add_dim('lat', 64)
ds.add_dim('lon', 128)

# Method 1: Explicit geospatial_bounds (highest priority)
ds.attrs['geospatial_bounds'] = {
    'type': 'Polygon',
    'coordinates': [[
        [-120, 30], [110, 30], [110, 50], [-120, 50], [-120, 30]
    ]]
}

# Method 2: From coordinates (used if geospatial_bounds not present)
ds.add_coord('lat', ['lat'], data=np.linspace(-45, 45, 64))
ds.add_coord('lon', ['lon'], data=np.linspace(-90, 90, 128))

# Extract bbox for STAC
item = ds.to_stac_item(id='auto-bbox')
print(f"Bounding box: {item.bbox}")
# If geospatial_bounds exists: uses those coordinates
# Otherwise: [-90, -45, 90, 45] from coordinates
```

### Manual Bbox Specification

Explicitly provide a bounding box when creating STAC Items:

```python
item = ds.to_stac_item(
    id='manual-bbox',
    bbox=[-120, 30, -110, 40]  # [west, south, east, north]
)
```

## Spatial Validation

### Validating Spatial Metadata

Check if your dataset has valid spatial metadata:

```python
ds = DummyDataset()
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

ds.add_coord('lat', ['lat'], data=np.linspace(-90, 90, 180))
ds.add_coord('lon', ['lon'], data=np.linspace(-180, 180, 360))

# Validate spatial metadata
validation = ds.validate_spatial_metadata()

if validation['valid']:
    print("✓ Spatial metadata is valid")
    print(f"  Found: {validation['found']}")
else:
    print("✗ Spatial metadata has issues:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

### Validation Results

The validation returns a dictionary with:

```python
{
    'valid': True/False,
    'found': ['geospatial_bounds', 'lat_coordinate', 'lon_coordinate'],
    'issues': ['List of validation issues']
}
```

### Common Validation Issues

```python
# Issue 1: No spatial information
ds = DummyDataset()
validation = ds.validate_spatial_metadata()
# Result: {'valid': False, 'issues': ['No spatial information found']}

# Issue 2: Invalid geospatial_bounds format
ds.attrs['geospatial_bounds'] = "invalid"  # Should be dict
validation = ds.validate_spatial_metadata()
# Result: {'valid': False, 'issues': ['geospatial_bounds must be a dictionary']}

# Issue 3: Missing coordinates
ds.add_coord('lat', ['lat'], data=np.linspace(-90, 90, 180))
# Missing 'lon' coordinate
validation = ds.validate_spatial_metadata()
# Result: {'valid': False, 'issues': ['Found lat but missing lon coordinate']}
```

## Regional Datasets

### Defining Regional Extent

For regional datasets, specify the actual coverage area:

```python
# North America region
ds = DummyDataset()
ds.add_spatial_extent(
    lat_bounds=(25, 70),      # Southern US to Northern Canada
    lon_bounds=(-170, -50)    # Alaska to Newfoundland
)

# European region
ds.add_spatial_extent(
    lat_bounds=(35, 71),      # Mediterranean to Northern Scandinavia
    lon_bounds=(-10, 40)      # Atlantic to Eastern Europe
)

# Custom polygon for irregular regions
ds.attrs['geospatial_bounds'] = {
    'type': 'Polygon',
    'coordinates': [[
        [-125, 32], [-114, 32], [-114, 42], [-125, 42], [-125, 32]
    ]]
}
```

## Grid Specifications

### Regular Grids

Define regular latitude-longitude grids:

```python
ds = DummyDataset()

# 1-degree global grid
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)
ds.add_coord('lat', ['lat'], data=np.linspace(-89.5, 89.5, 180))
ds.add_coord('lon', ['lon'], data=np.linspace(-179.5, 179.5, 360))

# 0.25-degree regional grid
ds.add_dim('lat', 100)
ds.add_dim('lon', 200)
ds.add_coord('lat', ['lat'], data=np.linspace(30, 55, 100))
ds.add_coord('lon', ['lon'], data=np.linspace(-130, -80, 200))
```

### Grid Cell Centers vs Boundaries

Specify whether coordinates represent cell centers or boundaries:

```python
# Cell centers (most common)
ds.add_coord('lat', ['lat'],
             data=np.linspace(-89.5, 89.5, 180),
             attrs={
                 'bounds': 'lat_bnds',
                 'units': 'degrees_north'
             })

# Add cell boundaries if needed
ds.add_variable('lat_bnds', ['lat', 'bnds'],
                attrs={'long_name': 'latitude bounds'})
```

## Coordinate Reference Systems

### Geographic Coordinates (WGS84)

Most common for global datasets:

```python
ds.attrs.update({
    'crs': 'EPSG:4326',  # WGS84
    'crs_wkt': 'GEOGCS["WGS 84",DATUM["WGS_1984",...]]'
})
```

### Projected Coordinates

For datasets in projected coordinate systems:

```python
# Example: UTM Zone 10N
ds.attrs.update({
    'crs': 'EPSG:32610',
    'crs_wkt': 'PROJCS["WGS 84 / UTM zone 10N",...]',
    'grid_mapping_name': 'transverse_mercator'
})
```

## Best Practices

### 1. Always Include Coordinate Attributes

```python
ds.add_coord('lat', ['lat'],
             data=lat_data,
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude',
                 'long_name': 'Latitude',
                 'axis': 'Y'
             })

ds.add_coord('lon', ['lon'],
             data=lon_data,
             attrs={
                 'units': 'degrees_east',
                 'standard_name': 'longitude',
                 'long_name': 'Longitude',
                 'axis': 'X'
             })
```

### 2. Use CF-Compliant Naming

```python
# Good: CF-compliant standard names
attrs = {
    'standard_name': 'latitude',
    'units': 'degrees_north'
}

# Avoid: Non-standard naming
attrs = {
    'name': 'lat',  # Use 'standard_name' instead
    'unit': 'deg'   # Use 'units' with CF-compliant values
}
```

### 3. Validate Before Export

```python
# Always validate before creating STAC Items
validation = ds.validate_spatial_metadata()

if validation['valid']:
    item = ds.to_stac_item(id='validated-item')
else:
    print("Fix these issues first:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

### 4. Document Coordinate Systems

```python
ds.attrs.update({
    'geospatial_lat_min': -90.0,
    'geospatial_lat_max': 90.0,
    'geospatial_lon_min': -180.0,
    'geospatial_lon_max': 180.0,
    'geospatial_lat_units': 'degrees_north',
    'geospatial_lon_units': 'degrees_east',
    'geospatial_lat_resolution': 1.0,
    'geospatial_lon_resolution': 1.0
})
```

### 5. Handle Edge Cases

```python
# Datasets crossing the antimeridian
ds.add_coord('lon', ['lon'],
             data=np.linspace(170, 190, 100) % 360,  # Wraps to -170 to 10
             attrs={'units': 'degrees_east'})

# Polar datasets
ds.add_coord('lat', ['lat'],
             data=np.linspace(60, 90, 100),  # Northern hemisphere only
             attrs={'units': 'degrees_north'})
```

## Complete Example

Here's a complete example with comprehensive spatial metadata:

```python
from dummyxarray import DummyDataset
import numpy as np

# Create dataset
ds = DummyDataset()

# Define dimensions
ds.add_dim('time', 12)
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

# Add spatial coordinates with full metadata
ds.add_coord('lat', ['lat'],
             data=np.linspace(-89.5, 89.5, 180),
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude',
                 'long_name': 'Latitude',
                 'axis': 'Y',
                 'valid_min': -90.0,
                 'valid_max': 90.0
             })

ds.add_coord('lon', ['lon'],
             data=np.linspace(-179.5, 179.5, 360),
             attrs={
                 'units': 'degrees_east',
                 'standard_name': 'longitude',
                 'long_name': 'Longitude',
                 'axis': 'X',
                 'valid_min': -180.0,
                 'valid_max': 180.0
             })

# Add global spatial metadata
ds.attrs.update({
    'geospatial_lat_min': -90.0,
    'geospatial_lat_max': 90.0,
    'geospatial_lon_min': -180.0,
    'geospatial_lon_max': 180.0,
    'geospatial_lat_units': 'degrees_north',
    'geospatial_lon_units': 'degrees_east',
    'geospatial_lat_resolution': 1.0,
    'geospatial_lon_resolution': 1.0,
    'geospatial_vertical_min': 0.0,
    'geospatial_vertical_max': 0.0,
    'geospatial_vertical_units': 'meters',
    'geospatial_vertical_positive': 'up'
})

# Add explicit spatial extent
ds.add_spatial_extent(
    lat_bounds=(-90, 90),
    lon_bounds=(-180, 180)
)

# Validate spatial metadata
validation = ds.validate_spatial_metadata()
print(f"Validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
print(f"Found: {', '.join(validation['found'])}")

# Create STAC Item with automatic bbox extraction
item = ds.to_stac_item(
    id='global-dataset',
    properties={
        'resolution': '1-degree',
        'coverage': 'global'
    }
)

print(f"STAC Item bbox: {item.bbox}")
print(f"STAC Item geometry: {item.geometry['type']}")
```

## See Also

- [STAC Catalogs](stac-catalogs.md) - STAC catalog integration
- [Geospatial Workflows](geospatial-workflows.md) - End-to-end examples
- [CF Compliance](cf-compliance.md) - CF conventions for coordinates
- [CF Standards](cf-standards.md) - CF standard names and attributes
