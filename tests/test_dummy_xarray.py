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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
