"""
Shared pytest fixtures for dummyxarray tests.

This module provides common fixtures used across all test modules.
"""

import numpy as np
import pytest

from dummyxarray import DummyArray, DummyDataset

# ============================================================================
# Basic Fixtures
# ============================================================================


@pytest.fixture
def empty_dataset():
    """Create an empty DummyDataset."""
    return DummyDataset()


@pytest.fixture
def simple_dataset():
    """Create a simple DummyDataset with basic structure."""
    ds = DummyDataset()
    ds.add_dim("time", 10)
    ds.add_dim("lat", 64)
    ds.add_dim("lon", 128)
    return ds


@pytest.fixture
def dataset_with_coords():
    """Create a DummyDataset with coordinates."""
    ds = DummyDataset()
    ds.add_dim("time", 10)
    ds.add_dim("lat", 64)
    ds.add_dim("lon", 128)
    ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
    ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
    ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
    return ds


@pytest.fixture
def dataset_with_data():
    """Create a DummyDataset with coordinates and variables with data."""
    ds = DummyDataset()
    ds.add_dim("time", 10)
    ds.add_dim("lat", 5)
    ds.add_dim("lon", 8)

    # Add coordinates with data
    ds.add_coord("time", dims=["time"], data=np.arange(10))
    ds.add_coord("lat", dims=["lat"], data=np.linspace(-90, 90, 5))
    ds.add_coord("lon", dims=["lon"], data=np.linspace(-180, 180, 8))

    # Add variable with data
    ds.add_variable(
        "temperature",
        dims=["time", "lat", "lon"],
        data=np.random.randn(10, 5, 8),
        attrs={"units": "K", "long_name": "Air Temperature"},
    )

    return ds


@pytest.fixture
def cf_compliant_dataset():
    """Create a CF-compliant DummyDataset."""
    ds = DummyDataset()
    ds.set_global_attrs(Conventions="CF-1.8", title="Test Dataset")

    # Add dimensions
    ds.add_dim("time", 10)
    ds.add_dim("lat", 64)
    ds.add_dim("lon", 128)
    ds.add_dim("lev", 5)

    # Add coordinates with CF attributes
    ds.add_coord(
        "time",
        dims=["time"],
        attrs={
            "standard_name": "time",
            "units": "days since 2000-01-01",
            "axis": "T",
        },
    )
    ds.add_coord(
        "lat",
        dims=["lat"],
        attrs={
            "standard_name": "latitude",
            "units": "degrees_north",
            "axis": "Y",
        },
    )
    ds.add_coord(
        "lon",
        dims=["lon"],
        attrs={
            "standard_name": "longitude",
            "units": "degrees_east",
            "axis": "X",
        },
    )
    ds.add_coord(
        "lev",
        dims=["lev"],
        attrs={
            "standard_name": "air_pressure",
            "units": "hPa",
            "axis": "Z",
        },
    )

    # Add variable
    ds.add_variable(
        "temperature",
        dims=["time", "lev", "lat", "lon"],
        attrs={
            "standard_name": "air_temperature",
            "units": "K",
            "long_name": "Air Temperature",
        },
    )

    return ds


@pytest.fixture
def simple_array():
    """Create a simple DummyArray."""
    return DummyArray(dims=["time"], attrs={"units": "days"})


@pytest.fixture
def array_with_data():
    """Create a DummyArray with data."""
    return DummyArray(
        dims=["time", "lat"],
        attrs={"units": "K", "long_name": "Temperature"},
        data=np.random.randn(10, 5),
    )


# ============================================================================
# Parametrized Fixtures
# ============================================================================


@pytest.fixture(params=[True, False])
def with_history(request):
    """Parametrize tests with/without history tracking."""
    return request.param


@pytest.fixture(params=["text", "dot", "mermaid"])
def viz_format(request):
    """Parametrize visualization formats."""
    return request.param


# ============================================================================
# Temporary File Fixtures
# ============================================================================


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Provide a temporary YAML file path."""
    return tmp_path / "test_dataset.yaml"


@pytest.fixture
def temp_zarr_store(tmp_path):
    """Provide a temporary Zarr store path."""
    return tmp_path / "test_dataset.zarr"


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def sample_history():
    """Provide sample operation history."""
    return [
        {"func": "__init__", "args": {}},
        {"func": "add_dim", "args": {"name": "time", "size": 10}},
        {"func": "add_coord", "args": {"name": "time", "dims": ["time"]}},
    ]


@pytest.fixture
def sample_provenance():
    """Provide sample provenance information."""
    return {
        "added": ["time"],
        "removed": [],
        "modified": {},
        "renamed": {},
    }
