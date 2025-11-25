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
├── __init__.py (9 lines)           # Public API exports
├── core.py (896 lines)             # Core classes (DummyArray, DummyDataset)
├── history.py (331 lines)          # HistoryMixin
├── provenance.py (157 lines)       # ProvenanceMixin
├── cf_compliance.py (318 lines)    # CFComplianceMixin
├── cf_standards.py (388 lines)     # CFStandardsMixin
├── io.py (246 lines)               # IOMixin
├── validation.py (82 lines)        # ValidationMixin
├── data_generation.py (169 lines)  # DataGenerationMixin
├── mfdataset.py (454 lines)        # Multi-file dataset support
├── time_utils.py (346 lines)       # Time calculation utilities
└── ncdump_parser.py (280 lines)    # NetCDF metadata parser
```

### Architecture Evolution

#### Phase 1 (Initial Refactoring)

- **Before**: Single file with 2041 lines
- **After**: 7 focused modules, average ~230 lines each

#### Current State (Phase 2)

- **12 modules**: Total 3,676 lines
- **Average**: ~306 lines per module
- **New capabilities**: Multi-file datasets, time-based grouping, CF standards
- **Maintainability**: Each module remains focused and testable
- **Scalability**: New features added as new modules (mfdataset, time_utils)

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
    CFStandardsMixin,
    IOMixin,
    ValidationMixin,
    DataGenerationMixin,
    FileTrackerMixin,
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

### CFStandardsMixin

**Purpose**: CF standard names and vocabulary support

**Location**: `cf_standards.py` (388 lines)

**Methods**:
- `validate_standard_names()` - Validate CF standard names
- `get_standard_name_info()` - Get standard name metadata
- `suggest_standard_names()` - Suggest appropriate standard names

**Features**:
- Access to CF standard name table
- Validation against official CF vocabulary
- Metadata lookup for standard names

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

### FileTrackerMixin

**Purpose**: Track source files in multi-file datasets

**Location**: `core.py` (part of core module)

**Methods**:
- `enable_file_tracking()` - Enable file tracking
- `add_file_source()` - Register a file source
- `get_source_files()` - Query files by coordinate range
- `get_file_info()` - Get metadata for a specific file
- `get_all_file_info()` - Get all tracked files

**Features**:
- Track which files contain which coordinate ranges
- Query files for specific time/coordinate slices
- Preserve file provenance in grouped datasets

## Method Resolution Order (MRO)

Python resolves methods left-to-right through the inheritance chain:

```python
DummyDataset.__mro__
# (DummyDataset, HistoryMixin, ProvenanceMixin, CFComplianceMixin,
#  CFStandardsMixin, IOMixin, ValidationMixin, DataGenerationMixin,
#  FileTrackerMixin, object)
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
│   ├── test_data_generation.py   # DataGenerationMixin
│   ├── test_mfdataset.py         # Multi-file dataset support
│   └── test_ncdump_parser.py     # NetCDF metadata parser
└── integration/                   # Integration tests
    └── test_workflows.py         # End-to-end workflows
```

**Total**: 188 tests with comprehensive coverage

See [Testing Documentation](testing.md) for details.

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

## Utility Modules

### time_utils.py

**Purpose**: Time calculation utilities for multi-file datasets

**Location**: `time_utils.py` (346 lines)

**Functions**:
- `infer_time_frequency()` - Detect time frequency from coordinate values
- `count_timesteps()` - Calculate timesteps between dates
- `add_frequency()` - Add time periods to dates
- `create_time_periods()` - Generate time period ranges
- `check_time_range_overlap()` - Check if time ranges overlap

**Features**:
- Full cftime calendar support (standard, noleap, 360_day, etc.)
- Handles extended time ranges beyond pandas limits
- CF-compliant time unit parsing

### mfdataset.py

**Purpose**: Multi-file dataset support

**Location**: `mfdataset.py` (454 lines)

**Functions**:
- `open_mfdataset()` - Open multiple NetCDF files as one dataset
- `groupby_time_impl()` - Group dataset by time periods
- `_read_file_metadata()` - Read metadata from NetCDF files
- `_combine_file_metadata()` - Combine metadata from multiple files
- `_create_time_subset_metadata()` - Create time-based subsets

**Features**:
- Metadata-only approach (no data loading)
- Automatic frequency inference
- Time-based grouping (decades, years, months, etc.)
- File tracking and provenance

### ncdump_parser.py

**Purpose**: Parse ncdump output for metadata extraction

**Location**: `ncdump_parser.py` (280 lines)

**Functions**:
- `parse_ncdump()` - Parse ncdump -h output
- `_parse_dimensions()` - Extract dimensions
- `_parse_variables()` - Extract variables
- `_parse_attributes()` - Extract attributes

**Features**:
- Alternative to opening NetCDF files directly
- Useful for remote or restricted file access
- Handles complex ncdump output formats

## Future Extensions

Potential additions:

- **CMIPMixin**: CMIP table integration and validation
- **BoundsMixin**: Automatic bounds generation for coordinates
- **PluginMixin**: Custom validator plugins
- **SpatialGroupingMixin**: Group by spatial regions

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
