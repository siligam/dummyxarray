# DummyDataset

The main class for creating and managing dataset metadata specifications.

`DummyDataset` is composed of multiple mixins that provide different functionality:

- **Core** - Basic dataset operations (dimensions, coordinates, variables)
- **[HistoryMixin](mixins/history.md)** - Operation tracking and replay
- **[ProvenanceMixin](mixins/provenance.md)** - Track what changed in operations
- **[CFComplianceMixin](mixins/cf-compliance.md)** - CF convention support
- **[IOMixin](mixins/io.md)** - Serialization and format conversion
- **[ValidationMixin](mixins/validation.md)** - Dataset structure validation
- **[DataGenerationMixin](mixins/data-generation.md)** - Generate realistic random data

## Class Reference

::: dummyxarray.DummyDataset
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      group_by_category: true
      show_category_heading: true
      show_bases: true
      heading_level: 3
