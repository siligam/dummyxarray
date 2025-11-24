# DataGenerationMixin

Provides realistic random data generation for testing and prototyping.

## Overview

The `DataGenerationMixin` populates datasets with realistic random data:

- **Smart generation** - Appropriate ranges based on variable type
- **Reproducible** - Use seeds for consistent results
- **Type-aware** - Different strategies for coordinates vs variables

## Key Methods

- `populate_with_random_data(seed=None)` - Fill all arrays with data
- `_generate_coordinate_data(coord_name, size)` - Generate coordinate data
- `_generate_variable_data(var_name, shape, attrs)` - Generate variable data

## Data Generation Strategies

### Coordinates

- **time** - Sequential integers (0, 1, 2, ...)
- **lat** - Uniform distribution from -90 to 90
- **lon** - Uniform distribution from -180 to 180
- **lev/plev** - Decreasing pressure levels
- **Default** - Sequential integers

### Variables

Based on variable name and units:

- **temperature** - Realistic ranges (250-310 K or -20-40°C)
- **precipitation** - Non-negative, skewed distribution
- **wind** - Appropriate ranges for wind components
- **humidity** - 0-100% range
- **Default** - Standard normal distribution

## Usage

```python
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_dim("lat", 64)
ds.add_coord("time", dims=["time"])
ds.add_coord("lat", dims=["lat"])
ds.add_variable("temperature", dims=["time", "lat"])

# Populate with random data
ds.populate_with_random_data(seed=42)

# Now all arrays have data
print(ds.coords["time"].data.shape)  # (10,)
print(ds.variables["temperature"].data.shape)  # (10, 64)
```

## API Reference

::: dummyxarray.data_generation.DataGenerationMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
