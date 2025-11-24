# Installation

## Using Pixi (Recommended)

[Pixi](https://pixi.sh) is a fast package manager that handles both Python and system dependencies.

```bash
# Clone the repository
git clone https://github.com/yourusername/dummyxarray.git
cd dummyxarray

# Install dependencies with pixi
pixi install

# Run tests to verify installation
pixi run test
```

## Using pip

If you prefer using pip, you can install the dependencies manually:

```bash
# Clone the repository
git clone https://github.com/yourusername/dummyxarray.git
cd dummyxarray

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Verify Installation

Test your installation by running:

```python
from dummyxarray import DummyDataset

ds = DummyDataset()
print("Installation successful!")
```

## Requirements

- Python >= 3.9
- numpy >= 1.20.0
- xarray >= 0.19.0
- pyyaml >= 5.4.0
- zarr >= 2.10.0

## Development Installation

For development, you'll also want pytest:

```bash
pixi install  # pytest is already included
```

Or with pip:

```bash
pip install pytest
```
