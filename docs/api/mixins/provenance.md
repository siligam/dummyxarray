# ProvenanceMixin

Tracks what changed in each operation (added, removed, modified, renamed).

## Overview

The `ProvenanceMixin` extends history tracking by recording detailed provenance information:

- **Added items** - New dimensions, coordinates, or variables
- **Removed items** - Deleted items
- **Modified items** - Changed attributes or data
- **Renamed items** - Name changes with old → new mapping

## Key Methods

- `get_provenance()` - Get provenance information for all operations
- `visualize_provenance(format)` - Visualize as 'compact' or 'detailed'

## Usage

```python
ds = DummyDataset()
ds.add_dim("time", 10)
ds.rename_dims(time="t")

# Get provenance
provenance = ds.get_provenance()
for op in provenance:
    print(f"{op['func']}: {op['provenance']}")
```

## API Reference

::: dummyxarray.provenance.ProvenanceMixin
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      heading_level: 3
