# CFComplianceMixin

Provides CF (Climate and Forecast) convention support.

## Overview

The `CFComplianceMixin` helps create CF-compliant datasets by:

- **Detecting axis types** - Automatically infer X, Y, Z, T axes
- **Validating metadata** - Check for CF compliance issues
- **Setting attributes** - Apply CF-standard axis attributes
- **Querying coordinates** - Find coordinates by axis type

## Key Methods

- `infer_axis()` - Detect axis types for all coordinates
- `set_axis_attributes()` - Set axis attributes on coordinates
- `get_axis_coordinates(axis)` - Get coordinates for specific axis
- `validate_cf(strict=False)` - Validate CF compliance

## Axis Detection

Axes are detected based on:

- **Coordinate names** - time, lat, lon, lev, etc.
- **Units** - degrees_north, days since, hPa, etc.
- **Standard names** - latitude, longitude, time, etc.

## Usage

See the [CF Compliance Guide](../../user-guide/cf-compliance.md) for detailed examples.

## API Reference

::: dummyxarray.cf_compliance.CFComplianceMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
