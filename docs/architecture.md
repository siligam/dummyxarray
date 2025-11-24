# Architecture

dummyxarray uses a modular, mixin-based architecture for maintainability and extensibility.

## Design Philosophy

The codebase follows these principles:

1. **Separation of Concerns** - Each module has a single, clear responsibility
2. **Composition over Inheritance** - Mixins provide functionality without deep hierarchies
3. **Maintainability** - Small, focused modules are easier to understand and modify
4. **Extensibility** - New features can be added as new mixins
5. **Testability** - Each mixin can be tested independently

## Module Structure

```
src/dummyxarray/
├── __init__.py                    # Public API exports
├── core.py (772 lines)            # Core classes and API
├── history.py (331 lines)         # HistoryMixin
├── provenance.py (157 lines)      # ProvenanceMixin
├── cf_compliance.py (318 lines)   # CFComplianceMixin
├── io.py (243 lines)              # IOMixin
├── validation.py (82 lines)       # ValidationMixin
└── data_generation.py (169 lines) # DataGenerationMixin
```

### Before Refactoring

- **Single file**: 2041 lines
- **Hard to navigate**: Everything in one place
- **Difficult to maintain**: Large monolithic class
- **Will grow**: Phase 2 would push to 3000+ lines

### After Refactoring

- **7 focused modules**: Average ~230 lines each
- **Easy to navigate**: Clear module boundaries
- **Easy to maintain**: Each module has one responsibility
- **Scalable**: New features = new mixins

## Core Classes

### DummyArray

Represents a single array (variable or coordinate) with metadata.

**Location**: `core.py`

**Attributes**:
- `dims` - List of dimension names
- `attrs` - Metadata dictionary
- `data` - Optional numpy array
- `encoding` - Encoding parameters

**Methods**:
- `infer_dims_from_data()` - Infer dimension names from shape
- `assign_attrs()` - Set attributes (xarray-compatible)
- `get_history()` - Get operation history
- `replay_history()` - Recreate from history

### DummyDataset

Main dataset class composed of multiple mixins.

**Location**: `core.py`

**Inheritance**:
```python
class DummyDataset(
    HistoryMixin,
    ProvenanceMixin,
    CFComplianceMixin,
    IOMixin,
    ValidationMixin,
    DataGenerationMixin,
):
    ...
```

**Core Attributes**:
- `dims` - Dictionary of dimension names to sizes
- `coords` - Dictionary of coordinate names to DummyArray
- `variables` - Dictionary of variable names to DummyArray
- `attrs` - Global attributes dictionary
- `_history` - Operation history (if tracking enabled)

**Core Methods** (in `core.py`):
- `add_dim()` - Add a dimension
- `add_coord()` - Add a coordinate
- `add_variable()` - Add a variable
- `assign_attrs()` - Set global attributes
- `rename_dims()`, `rename_vars()`, `rename()` - Renaming operations

## Mixins

### HistoryMixin

**Purpose**: Track and replay all dataset operations

**Location**: `history.py` (331 lines)

**Methods**:
- `_record_operation()` - Record an operation
- `get_history()` - Get operation list
- `export_history()` - Export as Python/JSON/YAML
- `replay_history()` - Recreate dataset from history
- `reset_history()` - Clear history
- `visualize_history()` - Visualize as text/DOT/Mermaid

**Dependencies**:
- Requires `self._history` attribute
- Used by all operations that modify the dataset

### ProvenanceMixin

**Purpose**: Track what changed in each operation

**Location**: `provenance.py` (157 lines)

**Methods**:
- `get_provenance()` - Get provenance information
- `visualize_provenance()` - Visualize changes

**Provenance Information**:
- `added` - Items added
- `removed` - Items removed
- `modified` - Items modified (before/after)
- `renamed` - Items renamed (old -> new)

### CFComplianceMixin

**Purpose**: CF convention support and validation

**Location**: `cf_compliance.py` (318 lines)

**Methods**:
- `infer_axis()` - Detect X/Y/Z/T axes
- `_detect_axis_type()` - Axis detection logic
- `set_axis_attributes()` - Set axis attributes
- `get_axis_coordinates()` - Query by axis
- `validate_cf()` - CF compliance validation

**Detection Rules**:
- Coordinate names (time, lat, lon, lev)
- Units (degrees_north, days since, etc.)
- Standard names (latitude, longitude, time)

### IOMixin

**Purpose**: Serialization and format conversion

**Location**: `io.py` (243 lines)

**Methods**:
- `to_dict()`, `to_json()`, `to_yaml()` - Export formats
- `save_yaml()`, `load_yaml()` - File I/O
- `from_xarray()` - Import from xarray
- `to_xarray()` - Convert to xarray
- `to_zarr()` - Write to Zarr

**Supported Formats**:
- Dictionary (Python native)
- JSON (human-readable, version control)
- YAML (human-readable, configuration)
- xarray.Dataset (interoperability)
- Zarr (cloud-optimized storage)

### ValidationMixin

**Purpose**: Dataset structure validation

**Location**: `validation.py` (82 lines)

**Methods**:
- `validate()` - Validate structure
- `_infer_and_register_dims()` - Auto-register dimensions

**Validation Checks**:
- Unknown dimensions
- Shape mismatches
- Missing coordinates (strict mode)

### DataGenerationMixin

**Purpose**: Generate realistic random data

**Location**: `data_generation.py` (169 lines)

**Methods**:
- `populate_with_random_data()` - Fill with data
- `_generate_coordinate_data()` - Coordinate data
- `_generate_variable_data()` - Variable data

**Smart Generation**:
- Time: Sequential integers
- Latitude: -90 to 90
- Longitude: -180 to 180
- Temperature: Realistic ranges based on units
- Precipitation: Non-negative, skewed distribution
- Wind: Appropriate ranges for components

## Method Resolution Order (MRO)

Python resolves methods left-to-right through the inheritance chain:

```python
DummyDataset.__mro__
# (DummyDataset, HistoryMixin, ProvenanceMixin, CFComplianceMixin,
#  IOMixin, ValidationMixin, DataGenerationMixin, object)
```

**Important**: No method name conflicts exist between mixins (verified during development).

## Adding New Mixins

To add a new mixin (e.g., for Phase 2 CMIP integration):

1. **Create the module**:
```python
# src/dummyxarray/cmip.py
class CMIPMixin:
    """CMIP table integration."""
    
    def validate_cmip_table(self, table_name):
        """Validate against CMIP table."""
        ...
    
    def map_to_cmip_vocabulary(self):
        """Map to CMIP vocabulary."""
        ...
```

2. **Add to DummyDataset**:
```python
# src/dummyxarray/core.py
from .cmip import CMIPMixin

class DummyDataset(
    HistoryMixin,
    ProvenanceMixin,
    CFComplianceMixin,
    CMIPMixin,  # ← Add here
    IOMixin,
    ValidationMixin,
    DataGenerationMixin,
):
    ...
```

3. **Create tests**:
```python
# tests/unit/test_cmip.py
class TestCMIPValidation:
    def test_validate_cmip_table(self):
        ...
```

## Testing Architecture

Tests mirror the source structure:

```
tests/
├── conftest.py                    # Shared fixtures
├── unit/                          # Unit tests per module
│   ├── test_core.py              # Core functionality
│   ├── test_history.py           # HistoryMixin
│   ├── test_provenance.py        # ProvenanceMixin
│   ├── test_cf_compliance.py     # CFComplianceMixin
│   ├── test_io.py                # IOMixin
│   ├── test_validation.py        # ValidationMixin
│   └── test_data_generation.py   # DataGenerationMixin
└── integration/                   # Integration tests
    └── test_workflows.py         # End-to-end workflows
```

**Total**: 159 tests with comprehensive coverage

See [Testing Documentation](../tests/README.md) for details.

## Design Patterns

### Mixin Pattern

**Advantages**:
- Composition over inheritance
- Clear separation of concerns
- Easy to add/remove features
- Independent testing

**Considerations**:
- Method name conflicts (avoided through naming conventions)
- Shared state through `self` attributes
- Order matters in MRO

### Dependency Injection

Mixins depend on attributes from `DummyDataset`:
- `self.dims`
- `self.coords`
- `self.variables`
- `self.attrs`
- `self._history`

### Factory Pattern

Class methods for alternative construction:
- `DummyDataset.from_xarray()`
- `DummyDataset.load_yaml()`
- `DummyDataset.replay_history()`

## Performance Considerations

- **History tracking**: Minimal overhead (~1% for typical operations)
- **Validation**: Only runs when explicitly called
- **Data generation**: Uses numpy for efficiency
- **Serialization**: JSON/YAML are human-readable but slower than pickle

## Future Extensions

Planned for Phase 2:

- **CMIPMixin**: CMIP table integration
- **VocabularyMixin**: Controlled vocabulary mapping
- **BoundsMixin**: Automatic bounds generation
- **PluginMixin**: Custom validator plugins

## Best Practices

1. **Keep mixins focused**: One responsibility per mixin
2. **Avoid method conflicts**: Use descriptive, specific names
3. **Document dependencies**: What attributes does the mixin need?
4. **Test independently**: Unit test each mixin
5. **Use private methods**: Prefix with `_` for internal helpers

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/stable/topics/class-based-views/mixins/) - Mixin inspiration
- [Python MRO](https://www.python.org/download/releases/2.3/mro/) - Method resolution order
- [Composition over Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) - Design principle
