# Geospatial Workflows

## Overview

This guide provides end-to-end examples of geospatial workflows using DummyXarray's STAC support, demonstrating real-world use cases from data creation to catalog publishing.

## Workflow 1: Climate Data Publishing

### Complete Climate Dataset Workflow

This example shows how to create, validate, and publish climate model output as STAC catalogs.

```python
from dummyxarray import DummyDataset
import numpy as np

# Step 1: Create dataset with spatial/temporal structure
ds = DummyDataset()

# Define dimensions
ds.add_dim('time', 365)
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

# Add time coordinate
ds.add_coord('time', ['time'],
             data=np.arange(365),
             attrs={
                 'units': 'days since 2020-01-01',
                 'calendar': 'gregorian',
                 'standard_name': 'time',
                 'long_name': 'Time'
             })

# Add spatial coordinates
ds.add_coord('lat', ['lat'],
             data=np.linspace(-89.5, 89.5, 180),
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude',
                 'long_name': 'Latitude'
             })

ds.add_coord('lon', ['lon'],
             data=np.linspace(-179.5, 179.5, 360),
             attrs={
                 'units': 'degrees_east',
                 'standard_name': 'longitude',
                 'long_name': 'Longitude'
             })

# Step 2: Add climate variables
ds.add_variable('temperature', ['time', 'lat', 'lon'],
                attrs={
                    'units': 'K',
                    'standard_name': 'air_temperature',
                    'long_name': 'Near-Surface Air Temperature'
                })

ds.add_variable('precipitation', ['time', 'lat', 'lon'],
                attrs={
                    'units': 'kg m-2 s-1',
                    'standard_name': 'precipitation_flux',
                    'long_name': 'Precipitation Flux'
                })

# Step 3: Add global metadata
ds.attrs.update({
    'title': 'Global Climate Model Output 2020',
    'institution': 'Climate Research Institute',
    'source': 'CESM2 Climate Model',
    'references': 'https://doi.org/10.xxxx/climate-2020',
    'comment': 'Daily global climate data at 1-degree resolution',
    'Conventions': 'CF-1.8',
    'history': f'Created on {np.datetime64("now")}'
})

# Step 4: Infer and validate spatial/temporal metadata
start, end = ds.infer_temporal_extent()
print(f"Temporal coverage: {start} to {end}")

validation = ds.validate_spatial_metadata()
if validation['valid']:
    print("✓ Spatial metadata validated")
else:
    print("✗ Spatial validation issues:")
    for issue in validation['issues']:
        print(f"  - {issue}")

# Step 5: Create STAC Item
item = ds.to_stac_item(
    id='climate-global-2020',
    properties={
        'model': 'CESM2',
        'experiment': 'historical',
        'frequency': 'daily',
        'realm': 'atmos',
        'institution_id': 'CRI'
    }
)

# Step 6: Save STAC catalog
ds.save_stac_item('climate_2020.json', id='climate-global-2020')
print("✓ STAC Item saved to climate_2020.json")

# Step 7: Create collection for multiple years
datasets = []
for year in range(2020, 2023):
    yearly_ds = DummyDataset()
    # ... configure yearly_ds ...
    yearly_ds.attrs['title'] = f'Climate Data {year}'
    datasets.append(yearly_ds)

collection = DummyDataset.create_stac_collection(
    datasets,
    collection_id='climate-2020-2022',
    description='Global climate data 2020-2022',
    license='CC-BY-4.0'
)

print(f"✓ Collection created with {len(list(collection.get_items()))} items")
```

## Workflow 2: Regional Satellite Data

### Processing Regional Satellite Imagery

This example demonstrates handling regional satellite data with specific geographic coverage.

```python
from dummyxarray import DummyDataset
import numpy as np

# Step 1: Define regional extent (North America)
ds = DummyDataset()

# Regional dimensions (0.25-degree resolution)
ds.add_dim('time', 1)
ds.add_dim('lat', 180)  # 25°N to 70°N
ds.add_dim('lon', 360)  # 170°W to 50°W

# Step 2: Add regional coordinates
ds.add_coord('lat', ['lat'],
             data=np.linspace(25, 70, 180),
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude'
             })

ds.add_coord('lon', ['lon'],
             data=np.linspace(-170, -50, 360),
             attrs={
                 'units': 'degrees_east',
                 'standard_name': 'longitude'
             })

# Step 3: Add satellite bands
ds.add_variable('red', ['time', 'lat', 'lon'],
                attrs={
                    'long_name': 'Red Band Reflectance',
                    'units': '1',
                    'wavelength': '0.665 micrometers'
                })

ds.add_variable('nir', ['time', 'lat', 'lon'],
                attrs={
                    'long_name': 'Near-Infrared Band Reflectance',
                    'units': '1',
                    'wavelength': '0.865 micrometers'
                })

# Step 4: Add spatial extent
ds.add_spatial_extent(
    lat_bounds=(25, 70),
    lon_bounds=(-170, -50)
)

# Step 5: Add satellite-specific metadata
ds.attrs.update({
    'title': 'Landsat 8 North America',
    'platform': 'Landsat-8',
    'instrument': 'OLI',
    'processing_level': 'L2',
    'cloud_cover': 5.2,
    'time_coverage_start': '2020-06-15T18:30:00Z',
    'time_coverage_end': '2020-06-15T18:30:00Z'
})

# Step 6: Create STAC Item with custom geometry
item = ds.to_stac_item(
    id='landsat8-na-20200615',
    properties={
        'eo:cloud_cover': 5.2,
        'platform': 'landsat-8',
        'instruments': ['oli'],
        'gsd': 30  # Ground sample distance in meters
    }
)

# Step 7: Save with satellite-specific metadata
ds.save_stac_item(
    'landsat8_na.json',
    id='landsat8-na-20200615',
    properties={
        'eo:bands': [
            {'name': 'red', 'common_name': 'red'},
            {'name': 'nir', 'common_name': 'nir'}
        ]
    }
)

print("✓ Regional satellite STAC Item created")
```

## Workflow 3: Multi-Resolution Dataset Collection

### Creating Collections with Multiple Resolutions

This example shows how to organize datasets at different spatial resolutions.

```python
from dummyxarray import DummyDataset
import numpy as np

def create_resolution_dataset(resolution_deg, name):
    """Create a dataset at a specific resolution."""
    ds = DummyDataset()
    
    # Calculate dimensions based on resolution
    nlat = int(180 / resolution_deg)
    nlon = int(360 / resolution_deg)
    
    ds.add_dim('time', 12)
    ds.add_dim('lat', nlat)
    ds.add_dim('lon', nlon)
    
    # Add coordinates
    ds.add_coord('lat', ['lat'],
                 data=np.linspace(-90 + resolution_deg/2, 
                                 90 - resolution_deg/2, nlat))
    ds.add_coord('lon', ['lon'],
                 data=np.linspace(-180 + resolution_deg/2,
                                 180 - resolution_deg/2, nlon))
    
    # Add variable
    ds.add_variable('temperature', ['time', 'lat', 'lon'],
                    attrs={'units': 'K', 'standard_name': 'air_temperature'})
    
    # Add metadata
    ds.attrs.update({
        'title': f'{name} - {resolution_deg}° resolution',
        'spatial_resolution': f'{resolution_deg} degrees',
        'grid_type': 'regular_lat_lon'
    })
    
    # Infer temporal extent
    ds.add_coord('time', ['time'],
                 data=np.arange(12),
                 attrs={'units': 'months since 2020-01-01'})
    ds.infer_temporal_extent()
    
    return ds

# Create datasets at different resolutions
coarse_ds = create_resolution_dataset(2.0, 'Coarse Resolution')
medium_ds = create_resolution_dataset(1.0, 'Medium Resolution')
fine_ds = create_resolution_dataset(0.5, 'Fine Resolution')

# Create multi-resolution collection
collection = DummyDataset.create_stac_collection(
    [coarse_ds, medium_ds, fine_ds],
    collection_id='multi-resolution-temperature',
    description='Temperature data at multiple spatial resolutions',
    license='CC-BY-4.0'
)

print(f"✓ Multi-resolution collection created")
print(f"  Resolutions: 2.0°, 1.0°, 0.5°")
```

## Workflow 4: Time Series with Spatial Coverage

### Monthly Time Series Dataset

This example demonstrates creating a time series of spatial datasets.

```python
from dummyxarray import DummyDataset
import numpy as np
from datetime import datetime, timedelta

def create_monthly_dataset(year, month):
    """Create a dataset for a specific month."""
    ds = DummyDataset()
    
    # Spatial dimensions
    ds.add_dim('lat', 180)
    ds.add_dim('lon', 360)
    
    # Add spatial coordinates
    ds.add_coord('lat', ['lat'], data=np.linspace(-89.5, 89.5, 180))
    ds.add_coord('lon', ['lon'], data=np.linspace(-179.5, 179.5, 360))
    
    # Add monthly data
    ds.add_variable('sst', ['lat', 'lon'],
                    attrs={
                        'units': 'degree_Celsius',
                        'standard_name': 'sea_surface_temperature',
                        'long_name': 'Sea Surface Temperature'
                    })
    
    # Add temporal metadata
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    ds.attrs.update({
        'title': f'SST {year}-{month:02d}',
        'time_coverage_start': start_date.isoformat() + 'Z',
        'time_coverage_end': end_date.isoformat() + 'Z',
        'temporal_resolution': 'monthly'
    })
    
    # Add spatial extent
    ds.add_spatial_extent(lat_bounds=(-90, 90), lon_bounds=(-180, 180))
    
    return ds

# Create monthly datasets for 2020
monthly_datasets = []
for month in range(1, 13):
    ds = create_monthly_dataset(2020, month)
    monthly_datasets.append(ds)

# Create time series collection
collection = DummyDataset.create_stac_collection(
    monthly_datasets,
    collection_id='sst-monthly-2020',
    description='Monthly sea surface temperature for 2020',
    license='CC-BY-4.0'
)

print(f"✓ Time series collection created with {len(monthly_datasets)} months")
```

## Workflow 5: Data Validation Pipeline

### Complete Validation and Quality Control

This example shows a comprehensive validation pipeline before publishing.

```python
from dummyxarray import DummyDataset
import numpy as np

def validate_dataset_for_stac(ds, dataset_id):
    """Comprehensive validation before STAC export."""
    print(f"\n=== Validating {dataset_id} ===")
    
    issues = []
    
    # 1. Check spatial metadata
    spatial_validation = ds.validate_spatial_metadata()
    if not spatial_validation['valid']:
        issues.extend(spatial_validation['issues'])
        print("✗ Spatial validation failed:")
        for issue in spatial_validation['issues']:
            print(f"  - {issue}")
    else:
        print(f"✓ Spatial metadata valid: {', '.join(spatial_validation['found'])}")
    
    # 2. Check temporal metadata
    if 'time_coverage_start' not in ds.attrs:
        issues.append("Missing time_coverage_start")
        print("✗ Missing temporal coverage start")
    else:
        print(f"✓ Temporal coverage: {ds.attrs['time_coverage_start']}")
    
    # 3. Check required global attributes
    required_attrs = ['title', 'description']
    for attr in required_attrs:
        if attr not in ds.attrs:
            issues.append(f"Missing required attribute: {attr}")
            print(f"✗ Missing {attr}")
        else:
            print(f"✓ Has {attr}")
    
    # 4. Check coordinate attributes
    if 'lat' in ds.coords:
        lat_coord = ds.coords['lat']
        if 'units' not in lat_coord.attrs:
            issues.append("Latitude missing units")
            print("✗ Latitude missing units")
        else:
            print(f"✓ Latitude units: {lat_coord.attrs['units']}")
    
    # 5. Check variable metadata
    for var_name, var in ds.variables.items():
        if 'units' not in var.attrs:
            issues.append(f"Variable {var_name} missing units")
            print(f"✗ Variable {var_name} missing units")
        else:
            print(f"✓ Variable {var_name} has units: {var.attrs['units']}")
    
    # Summary
    if not issues:
        print("\n✓✓✓ All validation checks passed!")
        return True
    else:
        print(f"\n✗✗✗ Found {len(issues)} issues")
        return False

# Example usage
ds = DummyDataset()
ds.add_dim('lat', 180)
ds.add_dim('lon', 360)

ds.add_coord('lat', ['lat'],
             data=np.linspace(-89.5, 89.5, 180),
             attrs={'units': 'degrees_north', 'standard_name': 'latitude'})
ds.add_coord('lon', ['lon'],
             data=np.linspace(-179.5, 179.5, 360),
             attrs={'units': 'degrees_east', 'standard_name': 'longitude'})

ds.add_variable('temperature', ['lat', 'lon'],
                attrs={'units': 'K', 'standard_name': 'air_temperature'})

ds.attrs.update({
    'title': 'Global Temperature',
    'description': 'Global temperature analysis',
    'time_coverage_start': '2020-01-01T00:00:00Z'
})

ds.add_spatial_extent(lat_bounds=(-90, 90), lon_bounds=(-180, 180))

# Validate before export
if validate_dataset_for_stac(ds, 'temperature-global'):
    item = ds.to_stac_item(id='temperature-global')
    ds.save_stac_item('validated_temperature.json', id='temperature-global')
    print("\n✓ STAC Item created and saved")
else:
    print("\n✗ Fix validation issues before creating STAC Item")
```

## Workflow 6: Integration with Existing Data

### Converting Existing Metadata to STAC

This example shows how to convert existing dataset metadata to STAC format.

```python
from dummyxarray import DummyDataset
import numpy as np

# Simulate loading existing dataset metadata
existing_metadata = {
    'dataset_name': 'ERA5 Reanalysis',
    'variables': ['temperature', 'pressure', 'humidity'],
    'lat_min': -90, 'lat_max': 90,
    'lon_min': -180, 'lon_max': 180,
    'time_start': '2020-01-01',
    'time_end': '2020-12-31',
    'resolution': '0.25 degrees',
    'source': 'ECMWF ERA5',
    'license': 'Copernicus License'
}

# Convert to DummyDataset
ds = DummyDataset()

# Add dimensions based on resolution
resolution = 0.25
nlat = int(180 / resolution)
nlon = int(360 / resolution)

ds.add_dim('time', 365)
ds.add_dim('lat', nlat)
ds.add_dim('lon', nlon)

# Add coordinates
ds.add_coord('lat', ['lat'],
             data=np.linspace(existing_metadata['lat_min'],
                            existing_metadata['lat_max'], nlat))
ds.add_coord('lon', ['lon'],
             data=np.linspace(existing_metadata['lon_min'],
                            existing_metadata['lon_max'], nlon))

# Add variables from metadata
for var_name in existing_metadata['variables']:
    ds.add_variable(var_name, ['time', 'lat', 'lon'])

# Convert metadata to STAC-compatible format
ds.attrs.update({
    'title': existing_metadata['dataset_name'],
    'description': f"{existing_metadata['dataset_name']} at {existing_metadata['resolution']}",
    'source': existing_metadata['source'],
    'license': existing_metadata['license'],
    'time_coverage_start': existing_metadata['time_start'] + 'T00:00:00Z',
    'time_coverage_end': existing_metadata['time_end'] + 'T23:59:59Z',
    'spatial_resolution': existing_metadata['resolution']
})

# Add spatial extent
ds.add_spatial_extent(
    lat_bounds=(existing_metadata['lat_min'], existing_metadata['lat_max']),
    lon_bounds=(existing_metadata['lon_min'], existing_metadata['lon_max'])
)

# Create STAC Item
item = ds.to_stac_item(
    id='era5-reanalysis-2020',
    properties={
        'provider': 'ECMWF',
        'product': 'ERA5',
        'resolution': existing_metadata['resolution']
    }
)

print(f"✓ Converted {existing_metadata['dataset_name']} to STAC")
print(f"  Variables: {', '.join(existing_metadata['variables'])}")
print(f"  Coverage: {existing_metadata['time_start']} to {existing_metadata['time_end']}")
```

## Best Practices Summary

### 1. Always Validate Before Publishing

```python
validation = ds.validate_spatial_metadata()
if validation['valid']:
    item = ds.to_stac_item(id='validated-item')
```

### 2. Include Comprehensive Metadata

```python
ds.attrs.update({
    'title': 'Descriptive Title',
    'description': 'Detailed description',
    'institution': 'Data Provider',
    'source': 'Data Source',
    'references': 'DOI or URL',
    'license': 'CC-BY-4.0'
})
```

### 3. Use Standard Coordinate Attributes

```python
ds.add_coord('lat', ['lat'],
             data=lat_data,
             attrs={
                 'units': 'degrees_north',
                 'standard_name': 'latitude',
                 'axis': 'Y'
             })
```

### 4. Document Temporal Coverage

```python
ds.attrs.update({
    'time_coverage_start': '2020-01-01T00:00:00Z',
    'time_coverage_end': '2020-12-31T23:59:59Z',
    'temporal_resolution': 'daily'
})
```

### 5. Organize Collections Logically

```python
# Group by time period
collection = DummyDataset.create_stac_collection(
    yearly_datasets,
    collection_id='climate-2020-2025'
)

# Group by variable
collection = DummyDataset.create_stac_collection(
    [temp_ds, precip_ds, wind_ds],
    collection_id='atmospheric-variables'
)
```

## See Also

- [STAC Catalogs](stac-catalogs.md) - STAC catalog API reference
- [Spatial Metadata](spatial-metadata.md) - Spatial metadata handling
- [CF Compliance](cf-compliance.md) - CF conventions
- [Intake Catalogs](intake-catalogs.md) - Alternative catalog format
