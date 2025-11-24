# ValidationMixin

Provides dataset structure validation functionality.

## Overview

The `ValidationMixin` validates dataset structure to catch errors early:

- **Dimension checks** - Ensure all referenced dimensions exist
- **Shape validation** - Verify data shapes match dimension sizes
- **Coordinate checks** - Validate coordinate presence (strict mode)

## Key Methods

- `validate(strict=False)` - Validate dataset structure
- `_infer_and_register_dims(name, dims, data)` - Internal dimension inference

## Validation Checks

### Basic Validation

- Unknown dimensions referenced by variables/coordinates
- Shape mismatches between data and declared dimensions

### Strict Mode

When `strict=True`:

- All dimensions must have corresponding coordinates
- Raises `ValueError` on any validation failure

## Usage

```python
ds = DummyDataset()
ds.add_dim("time", 10)
ds.add_variable("temp", dims=["time", "lat"])  # Error: 'lat' not defined

# Validate
try:
    ds.validate()
except ValueError as e:
    print(f"Validation error: {e}")

# Strict validation
ds.validate(strict=True)  # Raises error if issues found
```

## API Reference

::: dummyxarray.validation.ValidationMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
