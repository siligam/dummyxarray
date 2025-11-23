"""
Tests for DummyDataset and DummyArray classes
"""

import pytest
import numpy as np
from dummyxarray import DummyArray, DummyDataset


class TestDummyArray:
    """Tests for DummyArray class"""

    def test_init_empty(self):
        """Test creating an empty DummyArray"""
        arr = DummyArray()
        assert arr.dims is None
        assert arr.attrs == {}
        assert arr.data is None
        assert arr.encoding == {}

    def test_init_with_params(self):
        """Test creating DummyArray with parameters"""
        arr = DummyArray(
            dims=["time", "lat"],
            attrs={"units": "K"},
            data=np.array([[1, 2], [3, 4]]),
            encoding={"dtype": "float32"}
        )
        assert arr.dims == ["time", "lat"]
        assert arr.attrs == {"units": "K"}
        assert arr.data is not None
        assert arr.encoding == {"dtype": "float32"}

    def test_infer_dims_from_data(self):
        """Test automatic dimension inference"""
        data = np.random.rand(3, 4, 5)
        arr = DummyArray(data=data)
        inferred = arr.infer_dims_from_data()
        
        assert arr.dims == ["dim_0", "dim_1", "dim_2"]
        assert inferred == {"dim_0": 3, "dim_1": 4, "dim_2": 5}

    def test_to_dict(self):
        """Test dictionary export"""
        arr = DummyArray(
            dims=["time"],
            attrs={"units": "days"},
            data=np.array([1, 2, 3])
        )
        result = arr.to_dict()
        
        assert result["dims"] == ["time"]
        assert result["attrs"] == {"units": "days"}
        assert result["has_data"] is True

    def test_repr_without_data(self):
        """Test repr for DummyArray without data"""
        arr = DummyArray(dims=["time", "lat"], attrs={"units": "K"})
        repr_str = repr(arr)
        
        assert "<dummyxarray.DummyArray>" in repr_str
        assert "Dimensions: (time, lat)" in repr_str
        assert "Data: None" in repr_str
        assert "units: K" in repr_str

    def test_repr_with_data(self):
        """Test repr for DummyArray with data"""
        arr = DummyArray(
            dims=["time"],
            attrs={"units": "K"},
            data=np.array([1, 2, 3, 4, 5])
        )
        repr_str = repr(arr)
        
        assert "<dummyxarray.DummyArray>" in repr_str
        assert "Dimensions: (time)" in repr_str
        assert "Shape: (5,)" in repr_str
        assert "dtype:" in repr_str
        assert "Data:" in repr_str
    
    def test_assign_attrs(self):
        """Test assign_attrs method for DummyArray"""
        arr = DummyArray(dims=["time"])
        
        # Test basic assignment
        result = arr.assign_attrs(units="K", long_name="Temperature")
        assert result is arr  # Should return self
        assert arr.attrs["units"] == "K"
        assert arr.attrs["long_name"] == "Temperature"
        
        # Test chaining
        arr.assign_attrs(standard_name="air_temperature").assign_attrs(cell_methods="time: mean")
        assert arr.attrs["standard_name"] == "air_temperature"
        assert arr.attrs["cell_methods"] == "time: mean"
        
        # Test updating existing attributes
        arr.assign_attrs(units="Celsius")
        assert arr.attrs["units"] == "Celsius"
        assert len(arr.attrs) == 4  # units, long_name, standard_name, cell_methods


class TestDummyDataset:
    """Tests for DummyDataset class"""

    def test_init_empty(self):
        """Test creating an empty dataset"""
        ds = DummyDataset()
        assert ds.dims == {}
        assert ds.coords == {}
        assert ds.variables == {}
        assert ds.attrs == {}

    def test_set_global_attrs(self):
        """Test setting global attributes"""
        ds = DummyDataset()
        ds.set_global_attrs(title="Test", institution="DKRZ")
        
        assert ds.attrs["title"] == "Test"
        assert ds.attrs["institution"] == "DKRZ"
    
    def test_assign_attrs(self):
        """Test assign_attrs method for DummyDataset (xarray-compatible API)"""
        ds = DummyDataset()
        
        # Test basic assignment
        result = ds.assign_attrs(title="Test Dataset", institution="DKRZ")
        assert result is ds  # Should return self for chaining
        assert ds.attrs["title"] == "Test Dataset"
        assert ds.attrs["institution"] == "DKRZ"
        
        # Test method chaining
        ds.assign_attrs(experiment="historical").assign_attrs(source="Model v1.0")
        assert ds.attrs["experiment"] == "historical"
        assert ds.attrs["source"] == "Model v1.0"
        
        # Test updating existing attributes
        ds.assign_attrs(title="Updated Title")
        assert ds.attrs["title"] == "Updated Title"
        assert len(ds.attrs) == 4  # title, institution, experiment, source
        
        # Test that it's equivalent to set_global_attrs
        ds2 = DummyDataset()
        ds2.set_global_attrs(title="Test")
        ds3 = DummyDataset()
        ds3.assign_attrs(title="Test")
        assert ds2.attrs == ds3.attrs

    def test_add_dim(self):
        """Test adding dimensions"""
        ds = DummyDataset()
        ds.add_dim("time", 12)
        ds.add_dim("lat", 180)
        
        assert ds.dims["time"] == 12
        assert ds.dims["lat"] == 180

    def test_add_coord(self):
        """Test adding coordinates"""
        ds = DummyDataset()
        ds.add_dim("lat", 3)
        ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
        
        assert "lat" in ds.coords
        assert ds.coords["lat"].dims == ["lat"]
        assert ds.coords["lat"].attrs["units"] == "degrees_north"

    def test_add_variable(self):
        """Test adding variables"""
        ds = DummyDataset()
        ds.add_dim("time", 12)
        ds.add_variable(
            "tas",
            ["time"],
            attrs={"units": "K", "long_name": "temperature"}
        )
        
        assert "tas" in ds.variables
        assert ds.variables["tas"].dims == ["time"]
        assert ds.variables["tas"].attrs["units"] == "K"

    def test_auto_dim_inference(self):
        """Test automatic dimension inference from data"""
        ds = DummyDataset()
        data = np.random.rand(5, 10)
        ds.add_variable("test_var", data=data)
        
        assert "dim_0" in ds.dims
        assert "dim_1" in ds.dims
        assert ds.dims["dim_0"] == 5
        assert ds.dims["dim_1"] == 10

    def test_dimension_mismatch_error(self):
        """Test that dimension size conflicts raise errors"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        
        data = np.random.rand(12)  # Wrong size
        with pytest.raises(ValueError, match="Dimension mismatch"):
            ds.add_variable("test", dims=["time"], data=data)

    def test_validate_unknown_dimension(self):
        """Test validation catches unknown dimensions"""
        ds = DummyDataset()
        ds.add_variable("bad_var", dims=["unknown_dim"])
        
        with pytest.raises(ValueError, match="Unknown dimension"):
            ds.validate()

    def test_validate_shape_mismatch(self):
        """Test validation catches shape mismatches during add_variable"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 5)
        
        # Add variable with wrong shape - should fail immediately
        data = np.random.rand(10, 6)  # Should be (10, 5)
        with pytest.raises(ValueError, match="Dimension mismatch"):
            ds.add_variable("test", dims=["time", "lat"], data=data)

    def test_validate_success(self):
        """Test successful validation"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        data = np.random.rand(10)
        ds.add_variable("test", dims=["time"], data=data)
        
        # Should not raise
        ds.validate()

    def test_to_dict(self):
        """Test dictionary export"""
        ds = DummyDataset()
        ds.set_global_attrs(title="Test Dataset")
        ds.add_dim("time", 5)
        ds.add_variable("tas", ["time"], attrs={"units": "K"})
        
        result = ds.to_dict()
        
        assert "dimensions" in result
        assert "variables" in result
        assert "attrs" in result
        assert result["dimensions"]["time"] == 5
        assert result["attrs"]["title"] == "Test Dataset"

    def test_to_yaml(self):
        """Test YAML export"""
        ds = DummyDataset()
        ds.add_dim("time", 3)
        ds.add_variable("test", ["time"])
        
        yaml_str = ds.to_yaml()
        assert "dimensions:" in yaml_str
        assert "time: 3" in yaml_str

    def test_to_json(self):
        """Test JSON export"""
        ds = DummyDataset()
        ds.add_dim("time", 3)
        
        json_str = ds.to_json()
        assert '"dimensions"' in json_str
        assert '"time": 3' in json_str

    def test_save_load_yaml(self, tmp_path):
        """Test saving and loading YAML specifications"""
        ds = DummyDataset()
        ds.set_global_attrs(title="Test")
        ds.add_dim("time", 12)
        ds.add_coord("time", ["time"], attrs={"units": "days"})
        ds.add_variable("tas", ["time"], attrs={"units": "K"})
        
        # Save
        yaml_path = tmp_path / "test_spec.yaml"
        ds.save_yaml(str(yaml_path))
        
        # Load
        loaded_ds = DummyDataset.load_yaml(str(yaml_path))
        
        assert loaded_ds.dims["time"] == 12
        assert loaded_ds.attrs["title"] == "Test"
        assert "time" in loaded_ds.coords
        assert "tas" in loaded_ds.variables

    def test_to_xarray_missing_data(self):
        """Test that to_xarray fails when data is missing"""
        ds = DummyDataset()
        ds.add_dim("time", 5)
        ds.add_variable("test", ["time"])  # No data
        
        with pytest.raises(ValueError, match="missing data"):
            ds.to_xarray()

    def test_to_xarray_success(self):
        """Test successful conversion to xarray"""
        ds = DummyDataset()
        ds.set_global_attrs(title="Test Dataset")
        
        time_data = np.arange(5)
        ds.add_coord("time", ["time"], data=time_data, attrs={"units": "days"})
        
        temp_data = np.random.rand(5)
        ds.add_variable("tas", ["time"], data=temp_data, attrs={"units": "K"})
        
        xr_ds = ds.to_xarray()
        
        assert "tas" in xr_ds.data_vars
        assert "time" in xr_ds.coords
        assert xr_ds.attrs["title"] == "Test Dataset"
        assert xr_ds["tas"].attrs["units"] == "K"

    def test_encoding_preserved(self):
        """Test that encoding is preserved in xarray conversion"""
        ds = DummyDataset()
        
        data = np.random.rand(10)
        ds.add_variable(
            "test",
            data=data,
            encoding={"dtype": "float32", "chunks": (5,)}
        )
        
        xr_ds = ds.to_xarray()
        
        assert xr_ds["test"].encoding["dtype"] == "float32"
        assert xr_ds["test"].encoding["chunks"] == (5,)

    def test_to_zarr(self, tmp_path):
        """Test writing to Zarr format"""
        ds = DummyDataset()
        
        time_data = np.arange(10)
        ds.add_coord("time", ["time"], data=time_data)
        
        temp_data = np.random.rand(10)
        ds.add_variable(
            "tas",
            ["time"],
            data=temp_data,
            encoding={"dtype": "float32"}
        )
        
        zarr_path = tmp_path / "test.zarr"
        ds.to_zarr(str(zarr_path))
        
        # Verify it was written
        assert zarr_path.exists()
        
        # Load it back with xarray
        import xarray as xr
        loaded = xr.open_zarr(str(zarr_path))
        assert "tas" in loaded.data_vars
        assert len(loaded["tas"]) == 10

    def test_from_xarray_without_data(self):
        """Test creating DummyDataset from xarray without data"""
        import xarray as xr
        
        # Create an xarray dataset
        xr_ds = xr.Dataset(
            data_vars={
                "temperature": (["time", "lat"], np.random.rand(10, 5),
                               {"units": "K", "long_name": "Temperature"})
            },
            coords={
                "time": (["time"], np.arange(10), {"units": "days"}),
                "lat": (["lat"], np.linspace(-90, 90, 5), {"units": "degrees_north"})
            },
            attrs={"title": "Test Dataset", "institution": "Test"}
        )
        
        # Convert to DummyDataset without data
        dummy_ds = DummyDataset.from_xarray(xr_ds, include_data=False)
        
        # Check structure
        assert dummy_ds.dims == {"time": 10, "lat": 5}
        assert "temperature" in dummy_ds.variables
        assert "time" in dummy_ds.coords
        assert "lat" in dummy_ds.coords
        
        # Check attributes
        assert dummy_ds.attrs["title"] == "Test Dataset"
        assert dummy_ds.variables["temperature"].attrs["units"] == "K"
        assert dummy_ds.coords["time"].attrs["units"] == "days"
        
        # Check that data is NOT included
        assert dummy_ds.variables["temperature"].data is None
        assert dummy_ds.coords["time"].data is None

    def test_from_xarray_with_data(self):
        """Test creating DummyDataset from xarray with data"""
        import xarray as xr
        
        # Create an xarray dataset
        temp_data = np.random.rand(10, 5)
        time_data = np.arange(10)
        
        xr_ds = xr.Dataset(
            data_vars={
                "temperature": (["time", "lat"], temp_data)
            },
            coords={
                "time": (["time"], time_data)
            }
        )
        
        # Convert to DummyDataset with data
        dummy_ds = DummyDataset.from_xarray(xr_ds, include_data=True)
        
        # Check that data IS included
        assert dummy_ds.variables["temperature"].data is not None
        assert dummy_ds.coords["time"].data is not None
        np.testing.assert_array_equal(
            dummy_ds.variables["temperature"].data, temp_data
        )
        np.testing.assert_array_equal(
            dummy_ds.coords["time"].data, time_data
        )

    def test_from_xarray_preserves_encoding(self):
        """Test that encoding is preserved when converting from xarray"""
        import xarray as xr
        
        # Create dataset with encoding
        xr_ds = xr.Dataset(
            data_vars={
                "temperature": (["time"], np.random.rand(10))
            }
        )
        xr_ds["temperature"].encoding = {"dtype": "float32", "chunks": (5,)}
        
        # Convert to DummyDataset
        dummy_ds = DummyDataset.from_xarray(xr_ds)
        
        # Check encoding is preserved
        assert dummy_ds.variables["temperature"].encoding["dtype"] == "float32"
        assert dummy_ds.variables["temperature"].encoding["chunks"] == (5,)

    def test_populate_with_random_data(self):
        """Test populating dataset with random data"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 5)
        ds.add_dim("lon", 8)
        
        # Add coordinates without data
        ds.add_coord("time", ["time"], attrs={"units": "days"})
        ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})
        
        # Add variable without data
        ds.add_variable("temperature", ["time", "lat", "lon"],
                       attrs={"units": "K", "standard_name": "air_temperature"})
        
        # Populate with random data
        ds.populate_with_random_data(seed=42)
        
        # Check that data was added
        assert ds.coords["time"].data is not None
        assert ds.coords["lat"].data is not None
        assert ds.coords["lon"].data is not None
        assert ds.variables["temperature"].data is not None
        
        # Check shapes
        assert ds.coords["time"].data.shape == (10,)
        assert ds.coords["lat"].data.shape == (5,)
        assert ds.coords["lon"].data.shape == (8,)
        assert ds.variables["temperature"].data.shape == (10, 5, 8)
        
        # Check coordinate data is meaningful
        assert np.all(ds.coords["lat"].data >= -90)
        assert np.all(ds.coords["lat"].data <= 90)
        assert np.all(ds.coords["lon"].data >= -180)
        assert np.all(ds.coords["lon"].data <= 180)
        
        # Check temperature is in reasonable range (Kelvin)
        assert np.all(ds.variables["temperature"].data >= 250)
        assert np.all(ds.variables["temperature"].data <= 310)

    def test_populate_with_random_data_reproducible(self):
        """Test that populate with seed is reproducible"""
        ds1 = DummyDataset()
        ds1.add_dim("time", 5)
        ds1.add_variable("temp", ["time"], attrs={"units": "K"})
        ds1.populate_with_random_data(seed=123)
        
        ds2 = DummyDataset()
        ds2.add_dim("time", 5)
        ds2.add_variable("temp", ["time"], attrs={"units": "K"})
        ds2.populate_with_random_data(seed=123)
        
        # Should be identical with same seed
        np.testing.assert_array_equal(
            ds1.variables["temp"].data,
            ds2.variables["temp"].data
        )

    def test_populate_different_variable_types(self):
        """Test that different variable types get appropriate data"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        
        # Add different types of variables
        ds.add_variable("tas", ["time"],
                       attrs={"standard_name": "air_temperature", "units": "K"})
        ds.add_variable("pr", ["time"],
                       attrs={"standard_name": "precipitation_flux"})
        ds.add_variable("psl", ["time"],
                       attrs={"standard_name": "air_pressure_at_sea_level"})
        
        ds.populate_with_random_data(seed=42)
        
        # Temperature should be in Kelvin range
        assert np.all(ds.variables["tas"].data >= 250)
        assert np.all(ds.variables["tas"].data <= 310)
        
        # Precipitation should be positive
        assert np.all(ds.variables["pr"].data >= 0)
        
        # Sea level pressure should be reasonable
        assert np.all(ds.variables["psl"].data >= 98000)
        assert np.all(ds.variables["psl"].data <= 104000)

    def test_populate_only_missing_data(self):
        """Test that populate doesn't overwrite existing data"""
        ds = DummyDataset()
        ds.add_dim("time", 5)
        
        # Add variable with existing data
        existing_data = np.array([1, 2, 3, 4, 5])
        ds.add_variable("existing", ["time"], data=existing_data)
        
        # Add variable without data
        ds.add_variable("new", ["time"])
        
        ds.populate_with_random_data(seed=42)
        
        # Existing data should not be changed
        np.testing.assert_array_equal(ds.variables["existing"].data, existing_data)
        
        # New variable should have data
        assert ds.variables["new"].data is not None

    def test_repr_empty(self):
        """Test repr for empty dataset"""
        ds = DummyDataset()
        repr_str = repr(ds)
        assert "<dummyxarray.DummyDataset>" in repr_str
        assert "Dimensions: ()" in repr_str

    def test_repr_with_content(self):
        """Test repr with dimensions, coords, and variables"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", ["time"], attrs={"units": "days"})
        ds.add_variable("temp", ["time"], attrs={"units": "K"})
        ds.set_global_attrs(title="Test Dataset")
        
        repr_str = repr(ds)
        
        # Check structure
        assert "<dummyxarray.DummyDataset>" in repr_str
        assert "Dimensions:" in repr_str
        assert "time: 10" in repr_str
        assert "Coordinates:" in repr_str
        assert "time" in repr_str
        assert "Data variables:" in repr_str
        assert "temp" in repr_str
        assert "Attributes:" in repr_str
        assert "title: Test Dataset" in repr_str
        
        # Check data indicators (no data yet)
        assert "✗" in repr_str

    def test_repr_with_data(self):
        """Test repr shows data presence correctly"""
        ds = DummyDataset()
        ds.add_dim("time", 5)
        ds.add_variable("temp", ["time"])
        
        # Before data
        repr_before = repr(ds)
        assert "✗" in repr_before
        assert "?" in repr_before
        
        # After data
        ds.populate_with_random_data(seed=42)
        repr_after = repr(ds)
        assert "✓" in repr_after
        assert "float64" in repr_after or "int64" in repr_after

    def test_attribute_access_coords(self):
        """Test attribute-style access for coordinates"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", ["time"], attrs={"units": "days"})
        
        # Access via attribute
        coord = ds.time
        assert coord is ds.coords["time"]
        assert coord.attrs["units"] == "days"

    def test_attribute_access_variables(self):
        """Test attribute-style access for variables"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("temperature", ["time"], attrs={"units": "K"})
        
        # Access via attribute
        var = ds.temperature
        assert var is ds.variables["temperature"]
        assert var.attrs["units"] == "K"

    def test_attribute_access_precedence(self):
        """Test that coordinates take precedence over variables"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", ["time"], attrs={"type": "coord"})
        # This would be unusual but test the precedence
        ds.add_variable("time", ["time"], attrs={"type": "var"})
        
        # Should get coordinate, not variable
        accessed = ds.time
        assert accessed is ds.coords["time"]
        assert accessed.attrs["type"] == "coord"

    def test_attribute_access_error(self):
        """Test that accessing non-existent attribute raises error"""
        ds = DummyDataset()
        
        with pytest.raises(AttributeError, match="no attribute 'nonexistent'"):
            _ = ds.nonexistent

    def test_attribute_set_error(self):
        """Test that setting attributes directly is not allowed"""
        ds = DummyDataset()
        
        with pytest.raises(AttributeError, match="Cannot set attribute"):
            ds.time = DummyArray()

    def test_dir_includes_coords_and_vars(self):
        """Test that dir() includes coordinates and variables"""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", ["time"])
        ds.add_variable("temperature", ["time"])
        
        dir_result = dir(ds)
        assert "time" in dir_result
        assert "temperature" in dir_result
        assert "coords" in dir_result
        assert "variables" in dir_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
