"""Tests for I/O functionality (IOMixin)."""

import json

import pytest
import yaml

from dummyxarray import DummyDataset


class TestDictExport:
    """Test dictionary export functionality."""

    def test_to_dict_empty(self, empty_dataset):
        """Test exporting empty dataset to dict."""
        result = empty_dataset.to_dict()

        assert "dimensions" in result
        assert "coordinates" in result
        assert "variables" in result
        assert "attrs" in result
        assert result["dimensions"] == {}

    def test_to_dict_with_data(self, dataset_with_coords):
        """Test exporting dataset with coordinates to dict."""
        result = dataset_with_coords.to_dict()

        assert result["dimensions"] == {"time": 10, "lat": 64, "lon": 128}
        assert "time" in result["coordinates"]
        assert "lat" in result["coordinates"]


class TestJSONExport:
    """Test JSON export functionality."""

    def test_to_json(self, simple_dataset):
        """Test JSON export."""
        json_str = simple_dataset.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "dimensions" in parsed
        assert parsed["dimensions"] == {"time": 10, "lat": 64, "lon": 128}

    def test_to_json_custom_kwargs(self, simple_dataset):
        """Test JSON export with custom arguments."""
        json_str = simple_dataset.to_json(indent=4)
        assert "    " in json_str  # Check for 4-space indent


class TestYAMLExport:
    """Test YAML export functionality."""

    def test_to_yaml(self, dataset_with_coords):
        """Test YAML export."""
        yaml_str = dataset_with_coords.to_yaml()

        # Should be valid YAML
        parsed = yaml.safe_load(yaml_str)
        assert "dimensions" in parsed
        assert "coordinates" in parsed

    def test_save_and_load_yaml(self, dataset_with_coords, temp_yaml_file):
        """Test saving and loading YAML files."""
        # Save
        dataset_with_coords.save_yaml(temp_yaml_file)
        assert temp_yaml_file.exists()

        # Load
        loaded = DummyDataset.load_yaml(temp_yaml_file)
        assert loaded.dims == dataset_with_coords.dims
        assert set(loaded.coords.keys()) == set(dataset_with_coords.coords.keys())


class TestXarrayConversion:
    """Test xarray conversion functionality."""

    def test_from_xarray_basic(self):
        """Test creating DummyDataset from xarray.Dataset."""
        import numpy as np
        import xarray as xr

        xr_ds = xr.Dataset({"temperature": (["time", "lat"], np.random.rand(10, 5))})

        dummy_ds = DummyDataset.from_xarray(xr_ds)
        assert dummy_ds.dims == {"time": 10, "lat": 5}
        assert "temperature" in dummy_ds.variables

    def test_from_xarray_with_data(self):
        """Test creating DummyDataset from xarray with data."""
        import numpy as np
        import xarray as xr

        data = np.random.rand(10, 5)
        xr_ds = xr.Dataset({"temperature": (["time", "lat"], data)})

        dummy_ds = DummyDataset.from_xarray(xr_ds, include_data=True)
        assert dummy_ds.variables["temperature"].data is not None

    def test_to_xarray(self, dataset_with_data):
        """Test converting DummyDataset to xarray.Dataset."""
        xr_ds = dataset_with_data.to_xarray()

        assert "temperature" in xr_ds
        assert xr_ds.dims == {"time": 10, "lat": 5, "lon": 8}

    def test_to_xarray_missing_data(self, dataset_with_coords):
        """Test that to_xarray fails when data is missing."""
        with pytest.raises(ValueError, match="missing data"):
            dataset_with_coords.to_xarray()


class TestZarrExport:
    """Test Zarr export functionality."""

    def test_to_zarr(self, dataset_with_data, temp_zarr_store):
        """Test writing to Zarr format."""
        dataset_with_data.to_zarr(temp_zarr_store)

        # Check that store was created
        assert temp_zarr_store.exists()

        # Verify we can read it back with xarray
        import xarray as xr

        loaded = xr.open_zarr(temp_zarr_store)
        assert "temperature" in loaded
