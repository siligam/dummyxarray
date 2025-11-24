# dummyxarray

[![CI](https://github.com/yourusername/fakexarray/workflows/CI/badge.svg)](https://github.com/yourusername/fakexarray/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A lightweight xarray-like object for building dataset metadata specifications.**

Define your dataset structure, metadata, and encoding before creating the actual data arrays. Perfect for planning datasets, generating templates, and ensuring CF compliance.

## Features

- 📋 **Metadata-first design** - Define structure before data
- 🔄 **xarray compatibility** - Convert to/from xarray.Dataset
- ✅ **CF compliance** - Axis detection, validation, standard names
- 📊 **Smart data generation** - Populate with realistic random data
- 📝 **History tracking** - Record and replay all operations
- 💾 **Multiple formats** - Export to YAML, JSON, Zarr, NetCDF
- 🎯 **Validation** - Catch errors before expensive operations

## Installation

```bash
# Using pixi (recommended)
pixi install

# Using pip
pip install -r requirements.txt
```

## Quick Start

```python
from dummyxarray import DummyDataset

# Create dataset structure
ds = DummyDataset()
ds.assign_attrs(Conventions="CF-1.8", title="My Dataset")

# Add dimensions and coordinates
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

# Add variable with encoding
ds.add_variable(
    "temperature",
    dims=["time", "lat", "lon"],
    attrs={"standard_name": "air_temperature", "units": "K"},
    encoding={"dtype": "float32", "chunks": (6, 32, 64)}
)

# Infer CF axis attributes
ds.infer_axis()
ds.set_axis_attributes()

# Validate CF compliance
result = ds.validate_cf()

# Populate with realistic data
ds.populate_with_random_data(seed=42)

# Convert to xarray or export
xr_ds = ds.to_xarray()
ds.to_zarr("output.zarr")
ds.save_yaml("template.yaml")
```

## Use Cases

**Dataset Planning** - Define structure and metadata before generating data

**Template Generation** - Create reusable dataset specifications

**CF Compliance** - Ensure metadata follows CF conventions

**Testing** - Generate realistic test datasets quickly

**Documentation** - Export human-readable dataset specifications

## Documentation

- **[User Guide](docs/user-guide.md)** - Detailed usage examples
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Examples](examples/)** - Working code examples
- **[CF Compliance](docs/cf-compliance.md)** - CF convention support

## Development

```bash
# Run tests
pixi run test

# Format code
pixi run format

# Lint code
pixi run lint

# Run all checks
pixi run check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
