# Features and Test Coverage

This document provides a comprehensive overview of all features and their test coverage.

## Feature Summary

| Feature | Description | Tests | Status |
|---------|-------------|-------|--------|
| **Basic Structure** | Define dimensions, coordinates, variables | 5 tests | ✅ |
| **Attribute Access** | xarray-style `ds.time` access | 6 tests | ✅ |
| **Rich Repr** | Interactive display for DummyArray and DummyDataset | 5 tests | ✅ |
| **Data Population** | Generate meaningful random data | 4 tests | ✅ |
| **from_xarray** | Extract metadata from xarray.Dataset | 3 tests | ✅ |
| **YAML/JSON Export** | Serialize to YAML/JSON | 3 tests | ✅ |
| **Validation** | Dimension and shape validation | 4 tests | ✅ |
| **xarray Conversion** | Convert to xarray.Dataset | 2 tests | ✅ |
| **Zarr Support** | Write directly to Zarr | 1 test | ✅ |
| **Encoding** | Preserve dtype, chunks, compression | 2 tests | ✅ |

**Total: 40 tests covering all features** ✅

## Detailed Test Coverage

### DummyArray Tests (6 tests)
- `test_init_empty` - Empty array initialization
- `test_init_with_params` - Array with parameters
- `test_infer_dims_from_data` - Automatic dimension inference
- `test_to_dict` - Dictionary export
- `test_repr_without_data` - Repr without data
- `test_repr_with_data` - Repr with data

### DummyDataset Tests (34 tests)

#### Basic Operations (6 tests)
- `test_init_empty` - Empty dataset initialization
- `test_set_global_attrs` - Global attributes
- `test_add_dim` - Add dimensions
- `test_add_coord` - Add coordinates
- `test_add_variable` - Add variables
- `test_auto_dim_inference` - Automatic dimension inference

#### Validation (4 tests)
- `test_dimension_mismatch_error` - Dimension mismatch detection
- `test_validate_unknown_dimension` - Unknown dimension detection
- `test_validate_shape_mismatch` - Shape mismatch detection
- `test_validate_success` - Successful validation

#### Serialization (4 tests)
- `test_to_dict` - Dictionary export
- `test_to_yaml` - YAML export
- `test_to_json` - JSON export
- `test_save_load_yaml` - Save and load from YAML

#### xarray Integration (5 tests)
- `test_to_xarray_missing_data` - Error when data missing
- `test_to_xarray_success` - Successful conversion
- `test_encoding_preserved` - Encoding preservation
- `test_to_zarr` - Zarr export
- `test_from_xarray_without_data` - Extract metadata only
- `test_from_xarray_with_data` - Extract with data
- `test_from_xarray_preserves_encoding` - Encoding preservation

#### Data Population (4 tests)
- `test_populate_with_random_data` - Basic population
- `test_populate_with_random_data_reproducible` - Reproducibility with seed
- `test_populate_different_variable_types` - Type-specific data
- `test_populate_only_missing_data` - Don't overwrite existing data

#### Rich Repr (5 tests)
- `test_repr_empty` - Empty dataset repr
- `test_repr_with_content` - Dataset with content
- `test_repr_with_data` - Data presence indicators

#### Attribute Access (6 tests)
- `test_attribute_access_coords` - Access coordinates as attributes
- `test_attribute_access_variables` - Access variables as attributes
- `test_attribute_access_precedence` - Coordinate precedence
- `test_attribute_access_error` - Error for non-existent attributes
- `test_attribute_set_error` - Prevent direct attribute setting
- `test_dir_includes_coords_and_vars` - Tab completion support

## Running Tests

```bash
# Run all tests
pixi run test

# Run with verbose output
pixi run test -v

# Run specific test
pixi run test -k test_attribute_access

# Run with coverage
pixi run test --cov=src/dummyxarray --cov-report=html
```

## Feature Usage Examples

See `README.md` for comprehensive usage examples of all features.

## Documentation

- **README.md** - Quick start and usage examples
- **docs/** - Full MkDocs documentation
- **example.py** - Basic usage example
- **example_from_xarray.py** - from_xarray() examples
- **example_populate.py** - Data population examples
