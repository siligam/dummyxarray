# Test Structure

This directory contains all tests for dummyxarray, organized by test type and module.

## Directory Structure

```
tests/
├── conftest.py                    # Shared fixtures and pytest configuration
├── unit/                          # Unit tests (per module)
│   ├── test_core.py              # DummyArray, DummyDataset core functionality
│   ├── test_history.py           # HistoryMixin tests
│   ├── test_provenance.py        # ProvenanceMixin tests
│   ├── test_cf_compliance.py     # CFComplianceMixin tests
│   ├── test_io.py                # IOMixin tests
│   ├── test_validation.py        # ValidationMixin tests
│   └── test_data_generation.py   # DataGenerationMixin tests
├── integration/                   # Integration tests (workflows)
│   └── test_workflows.py         # End-to-end workflow tests
└── fixtures/                      # Test data and fixtures
    └── __init__.py

```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual modules and mixins in isolation:

- **test_core.py**: Core classes (`DummyArray`, `DummyDataset`)
  - Initialization, repr, basic operations
  - Dimension management
  - Coordinate and variable management
  - Renaming operations

- **test_history.py**: History tracking functionality
  - Operation recording
  - History export/replay
  - History visualization (text, dot, mermaid)
  - Reset history

- **test_provenance.py**: Provenance tracking
  - Change tracking (added/removed/modified)
  - Provenance visualization
  - Rename tracking

- **test_cf_compliance.py**: CF convention support
  - Axis inference (X/Y/Z/T)
  - Axis attribute setting
  - CF validation
  - Standard name handling

- **test_io.py**: I/O operations
  - Dictionary/JSON/YAML export
  - File save/load
  - xarray conversion (to/from)
  - Zarr export

- **test_validation.py**: Dataset validation
  - Structure validation
  - Dimension inference
  - Conflict detection

- **test_data_generation.py**: Random data generation
  - Coordinate data generation
  - Variable data generation
  - Metadata-based generation

### Integration Tests (`tests/integration/`)

Test complete workflows and interactions between modules:

- **test_workflows.py**: End-to-end workflows
  - CF compliance workflow
  - History and provenance workflow
  - Data generation and export workflow
  - Rename workflow
  - Validation and fix workflow
  - Import/modify/export workflow

## Running Tests

### Run all tests
```bash
pixi run test
```

### Run specific test file
```bash
pixi run test tests/unit/test_core.py
```

### Run specific test class
```bash
pixi run test tests/unit/test_core.py::TestDummyArray
```

### Run specific test
```bash
pixi run test tests/unit/test_core.py::TestDummyArray::test_init_empty
```

### Run only unit tests
```bash
pixi run test tests/unit/
```

### Run only integration tests
```bash
pixi run test tests/integration/
```

### Run with markers
```bash
# Run only unit tests (if marked)
pytest -m unit

# Run only integration tests (if marked)
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with coverage
```bash
pytest --cov=dummyxarray --cov-report=html
```

## Shared Fixtures (`conftest.py`)

Common fixtures available to all tests:

### Dataset Fixtures
- `empty_dataset`: Empty DummyDataset
- `simple_dataset`: Dataset with dimensions only
- `dataset_with_coords`: Dataset with coordinates
- `dataset_with_data`: Dataset with data arrays
- `cf_compliant_dataset`: CF-compliant dataset

### Array Fixtures
- `simple_array`: Simple DummyArray
- `array_with_data`: DummyArray with data

### Parametrized Fixtures
- `with_history`: Test with/without history tracking
- `viz_format`: Test all visualization formats

### Temporary File Fixtures
- `temp_yaml_file`: Temporary YAML file path
- `temp_zarr_store`: Temporary Zarr store path

### Mock Data Fixtures
- `sample_history`: Sample operation history
- `sample_provenance`: Sample provenance data

## Writing New Tests

### Unit Test Template

```python
"""Tests for [module] functionality."""

import pytest
from dummyxarray import DummyDataset


class TestFeature:
    """Test [feature] functionality."""

    def test_basic_case(self, simple_dataset):
        """Test basic [feature] usage."""
        # Arrange
        ds = simple_dataset
        
        # Act
        result = ds.some_method()
        
        # Assert
        assert result is not None
```

### Integration Test Template

```python
"""Integration tests for [workflow]."""

import pytest
from dummyxarray import DummyDataset


class TestWorkflow:
    """Test [workflow] end-to-end."""

    def test_complete_workflow(self, tmp_path):
        """Test complete [workflow] from start to finish."""
        # Create dataset
        ds = DummyDataset()
        
        # Perform workflow steps
        ds.add_dim("time", 10)
        # ... more steps
        
        # Verify final state
        assert ds.dims["time"] == 10
```

## Best Practices

1. **Use fixtures**: Leverage shared fixtures from `conftest.py`
2. **Test one thing**: Each test should verify one specific behavior
3. **Descriptive names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern for clarity
5. **Parametrize**: Use `@pytest.mark.parametrize` for similar tests
6. **Mock external dependencies**: Don't rely on external services
7. **Clean up**: Use fixtures with cleanup or `tmp_path` for files

## Test Coverage

Current coverage: **159 tests** across all modules

- Unit tests: ~130 tests
- Integration tests: ~29 tests

Target: >90% code coverage
