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


class TestIntakeCatalog:
    """Test Intake catalog functionality."""

    def test_to_intake_catalog_basic(self, simple_dataset):
        """Test basic Intake catalog generation."""
        catalog_yaml = simple_dataset.to_intake_catalog()

        # Should be valid YAML
        parsed = yaml.safe_load(catalog_yaml)

        # Check structure
        assert "metadata" in parsed
        assert "sources" in parsed
        assert parsed["metadata"]["version"] == 1
        assert "dataset" in parsed["sources"]

        # Check source entry
        source = parsed["sources"]["dataset"]
        assert source["driver"] == "zarr"
        assert "description" in source
        assert "args" in source
        assert "urlpath" in source["args"]

    def test_to_intake_catalog_custom_params(self, dataset_with_coords):
        """Test Intake catalog with custom parameters."""
        catalog_yaml = dataset_with_coords.to_intake_catalog(
            name="climate_data",
            description="Climate model output",
            driver="netcdf",
            data_path="data/climate.nc",
            chunks={"time": 5},
        )

        parsed = yaml.safe_load(catalog_yaml)
        source = parsed["sources"]["climate_data"]

        assert source["description"] == "Climate model output"
        assert source["driver"] == "netcdf"
        assert source["args"]["urlpath"] == "data/climate.nc"
        assert source["args"]["chunks"] == {"time": 5}

    def test_to_intake_catalog_with_attrs(self, dataset_with_coords):
        """Test catalog includes dataset attributes."""
        dataset_with_coords.assign_attrs(
            title="Test Dataset", institution="Test Institution", Conventions="CF-1.8"
        )

        catalog_yaml = dataset_with_coords.to_intake_catalog()
        parsed = yaml.safe_load(catalog_yaml)

        # Check dataset attributes are included in metadata
        assert "dataset_attrs" in parsed["metadata"]
        attrs = parsed["metadata"]["dataset_attrs"]
        assert attrs["title"] == "Test Dataset"
        assert attrs["institution"] == "Test Institution"
        assert attrs["Conventions"] == "CF-1.8"

    def test_to_intake_catalog_with_structure_metadata(self, dataset_with_coords):
        """Test catalog includes dataset structure metadata."""
        # Add a variable with encoding
        dataset_with_coords.add_variable(
            "temperature",
            dims=["time", "lat", "lon"],
            attrs={"units": "K", "standard_name": "air_temperature"},
            encoding={"dtype": "float32", "chunks": (5, 32, 64)},
        )

        catalog_yaml = dataset_with_coords.to_intake_catalog()
        parsed = yaml.safe_load(catalog_yaml)

        # Check metadata section
        source_metadata = parsed["sources"]["dataset"]["metadata"]

        # Check dimensions
        assert "dimensions" in source_metadata
        assert source_metadata["dimensions"] == {"time": 10, "lat": 64, "lon": 128}

        # Check coordinates
        assert "coordinates" in source_metadata
        coords = source_metadata["coordinates"]
        assert "time" in coords
        assert coords["time"]["dims"] == ["time"]
        assert coords["time"]["attrs"]["units"] == "days since 2000-01-01"

        # Check variables
        assert "variables" in source_metadata
        vars_meta = source_metadata["variables"]
        assert "temperature" in vars_meta
        temp_meta = vars_meta["temperature"]
        assert temp_meta["dims"] == ["time", "lat", "lon"]
        assert temp_meta["attrs"]["units"] == "K"
        assert temp_meta["encoding"]["dtype"] == "float32"
        assert temp_meta["encoding"]["chunks"] == [5, 32, 64]

    def test_to_intake_catalog_empty_dataset(self, empty_dataset):
        """Test catalog generation with empty dataset."""
        catalog_yaml = empty_dataset.to_intake_catalog()
        parsed = yaml.safe_load(catalog_yaml)

        # Should still have basic structure
        assert "metadata" in parsed
        assert "sources" in parsed
        assert parsed["metadata"]["version"] == 1

        # Source should exist but have minimal metadata
        source = parsed["sources"]["dataset"]
        assert source["driver"] == "zarr"
        assert "metadata" not in source or source["metadata"] == {}

    def test_save_intake_catalog(self, simple_dataset, tmp_path):
        """Test saving Intake catalog to file."""
        catalog_path = tmp_path / "test_catalog.yaml"

        simple_dataset.save_intake_catalog(
            catalog_path, name="test_dataset", description="Test dataset for catalog"
        )

        # Check file exists
        assert catalog_path.exists()

        # Check content is valid YAML
        with open(catalog_path) as f:
            content = yaml.safe_load(f)

        assert "metadata" in content
        assert "sources" in content
        assert "test_dataset" in content["sources"]

    def test_save_intake_catalog_default_path(self, dataset_with_coords, tmp_path):
        """Test saving catalog with default data path template."""
        catalog_path = tmp_path / "catalog.yaml"

        dataset_with_coords.save_intake_catalog(catalog_path, name="my_dataset")

        with open(catalog_path) as f:
            content = yaml.safe_load(f)

        # Should use default template path
        assert (
            content["sources"]["my_dataset"]["args"]["urlpath"]
            == "{{ CATALOG_DIR }}/my_dataset.zarr"
        )

    def test_intake_catalog_yaml_format(self, simple_dataset):
        """Test that generated YAML is properly formatted."""
        catalog_yaml = simple_dataset.to_intake_catalog()

        # Should be valid YAML that can be parsed
        parsed = yaml.safe_load(catalog_yaml)
        assert isinstance(parsed, dict)

        # Should contain expected top-level keys
        assert set(parsed.keys()) == {"metadata", "sources"}

        # Should be string output
        assert isinstance(catalog_yaml, str)
        assert len(catalog_yaml) > 0

    def test_intake_catalog_with_complex_encoding(self, dataset_with_coords):
        """Test catalog with complex encoding information."""
        dataset_with_coords.add_variable(
            "data",
            dims=["time", "lat", "lon"],
            attrs={"long_name": "Sample data"},
            encoding={
                "dtype": "float32",
                "chunks": (5, 32, 64),
                "compressor": {"id": "zlib", "level": 5},
                "fill_value": None,
            },
        )

        catalog_yaml = dataset_with_coords.to_intake_catalog()
        parsed = yaml.safe_load(catalog_yaml)

        var_meta = parsed["sources"]["dataset"]["metadata"]["variables"]["data"]
        assert var_meta["encoding"]["dtype"] == "float32"
        assert var_meta["encoding"]["chunks"] == [5, 32, 64]
        assert var_meta["encoding"]["compressor"]["id"] == "zlib"
        assert var_meta["encoding"]["fill_value"] is None


class TestIntakeCatalogLoading:
    """Test Intake catalog loading functionality."""

    def test_from_intake_catalog_dict(self, dataset_with_coords):
        """Test loading DummyDataset from catalog dictionary."""
        # Create catalog from dataset
        catalog_yaml = dataset_with_coords.to_intake_catalog(
            name="test_data", description="Test dataset"
        )
        catalog_dict = yaml.safe_load(catalog_yaml)

        # Load dataset from catalog
        loaded_ds = DummyDataset.from_intake_catalog(catalog_dict, "test_data")

        # Check structure is preserved
        assert loaded_ds.dims == dataset_with_coords.dims
        assert set(loaded_ds.coords.keys()) == set(dataset_with_coords.coords.keys())
        assert loaded_ds.attrs["intake_catalog_source"] == "test_data"
        assert loaded_ds.attrs["intake_driver"] == "zarr"

    def test_from_intake_catalog_file(self, dataset_with_coords, tmp_path):
        """Test loading DummyDataset from catalog file."""
        # Save catalog to file
        catalog_path = tmp_path / "test_catalog.yaml"
        dataset_with_coords.save_intake_catalog(
            catalog_path, name="file_test", description="File test dataset"
        )

        # Load dataset from file
        loaded_ds = DummyDataset.from_intake_catalog(catalog_path, "file_test")

        # Check structure is preserved
        assert loaded_ds.dims == dataset_with_coords.dims
        assert set(loaded_ds.coords.keys()) == set(dataset_with_coords.coords.keys())
        assert loaded_ds.attrs["intake_catalog_source"] == "file_test"

    def test_from_intake_catalog_with_variables(self, dataset_with_coords):
        """Test loading catalog with variables and encoding."""
        # Add variable with encoding
        dataset_with_coords.add_variable(
            "temperature",
            dims=["time", "lat", "lon"],
            attrs={"units": "K", "standard_name": "air_temperature"},
            encoding={"dtype": "float32", "chunks": [5, 32, 64]},
        )

        # Create and load catalog
        catalog_yaml = dataset_with_coords.to_intake_catalog(name="var_test")
        catalog_dict = yaml.safe_load(catalog_yaml)
        loaded_ds = DummyDataset.from_intake_catalog(catalog_dict, "var_test")

        # Check variables are preserved
        assert "temperature" in loaded_ds.variables
        temp_var = loaded_ds.variables["temperature"]
        assert temp_var.dims == ["time", "lat", "lon"]
        assert temp_var.attrs["units"] == "K"
        assert temp_var.encoding["dtype"] == "float32"
        assert temp_var.encoding["chunks"] == [5, 32, 64]

    def test_from_intake_catalog_auto_source(self, simple_dataset):
        """Test automatic source selection when only one source exists."""
        catalog_yaml = simple_dataset.to_intake_catalog()
        catalog_dict = yaml.safe_load(catalog_yaml)

        # Should work without specifying source_name
        loaded_ds = DummyDataset.from_intake_catalog(catalog_dict)
        assert loaded_ds.attrs["intake_catalog_source"] == "dataset"

    def test_from_intake_catalog_multiple_sources_error(self):
        """Test error when multiple sources exist but no source_name specified."""
        catalog = {
            "metadata": {"version": 1},
            "sources": {
                "source1": {"driver": "zarr", "args": {"urlpath": "data1.zarr"}},
                "source2": {"driver": "zarr", "args": {"urlpath": "data2.zarr"}},
            },
        }

        with pytest.raises(ValueError, match="Multiple sources found"):
            DummyDataset.from_intake_catalog(catalog)

    def test_from_intake_catalog_source_not_found(self):
        """Test error when specified source_name doesn't exist."""
        catalog = {
            "metadata": {"version": 1},
            "sources": {"source1": {"driver": "zarr", "args": {"urlpath": "data1.zarr"}}},
        }

        with pytest.raises(ValueError, match="Source 'nonexistent' not found"):
            DummyDataset.from_intake_catalog(catalog, "nonexistent")

    def test_from_intake_catalog_invalid_input(self):
        """Test error handling for invalid catalog input."""
        with pytest.raises(ValueError, match="catalog_source must be"):
            DummyDataset.from_intake_catalog(123)

        # Test with invalid file path (should raise FileNotFoundError, not ValueError)
        with pytest.raises(FileNotFoundError, match="Catalog file not found"):
            DummyDataset.from_intake_catalog("invalid")

        with pytest.raises(ValueError, match="Catalog must contain 'sources'"):
            DummyDataset.from_intake_catalog({"metadata": {"version": 1}})

        with pytest.raises(ValueError, match="Catalog sources section cannot be empty"):
            DummyDataset.from_intake_catalog({"metadata": {"version": 1}, "sources": {}})

    def test_from_intake_catalog_file_not_found(self):
        """Test error when catalog file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Catalog file not found"):
            DummyDataset.from_intake_catalog("/nonexistent/path/catalog.yaml")

    def test_from_intake_catalog_preserves_dataset_attrs(self, dataset_with_coords):
        """Test that dataset attributes are preserved from catalog metadata."""
        # Add dataset attributes
        dataset_with_coords.assign_attrs(
            title="Test Title", institution="Test Institution", Conventions="CF-1.8"
        )

        # Create and load catalog
        catalog_yaml = dataset_with_coords.to_intake_catalog(name="attrs_test")
        catalog_dict = yaml.safe_load(catalog_yaml)
        loaded_ds = DummyDataset.from_intake_catalog(catalog_dict, "attrs_test")

        # Check dataset attributes are preserved
        assert loaded_ds.attrs["title"] == "Test Title"
        assert loaded_ds.attrs["institution"] == "Test Institution"
        assert loaded_ds.attrs["Conventions"] == "CF-1.8"
        assert loaded_ds.attrs["intake_catalog_source"] == "attrs_test"

    def test_load_intake_catalog_convenience(self, dataset_with_coords, tmp_path):
        """Test load_intake_catalog convenience method."""
        # Save catalog to file
        catalog_path = tmp_path / "convenience_test.yaml"
        dataset_with_coords.save_intake_catalog(
            catalog_path, name="convenience", description="Convenience test"
        )

        # Load using convenience method
        loaded_ds = DummyDataset.load_intake_catalog(catalog_path, "convenience")

        # Should work the same as from_intake_catalog
        assert loaded_ds.dims == dataset_with_coords.dims
        assert loaded_ds.attrs["intake_catalog_source"] == "convenience"

    def test_round_trip_catalog(self, dataset_with_coords):
        """Test complete round-trip: dataset -> catalog -> dataset."""
        # Add variable to make it more interesting
        dataset_with_coords.add_variable(
            "data",
            dims=["time", "lat", "lon"],
            attrs={"long_name": "Sample data"},
            encoding={"dtype": "float32", "chunks": [5, 32, 64]},
        )

        # Export to catalog
        catalog_yaml = dataset_with_coords.to_intake_catalog(
            name="round_trip", description="Round trip test"
        )
        catalog_dict = yaml.safe_load(catalog_yaml)

        # Import from catalog
        loaded_ds = DummyDataset.from_intake_catalog(catalog_dict, "round_trip")

        # Compare structures
        assert loaded_ds.dims == dataset_with_coords.dims
        assert set(loaded_ds.coords.keys()) == set(dataset_with_coords.coords.keys())
        assert set(loaded_ds.variables.keys()) == set(dataset_with_coords.variables.keys())

        # Check variable details
        orig_var = dataset_with_coords.variables["data"]
        loaded_var = loaded_ds.variables["data"]
        assert loaded_var.dims == orig_var.dims
        assert loaded_var.attrs == orig_var.attrs
        assert loaded_var.encoding == orig_var.encoding
