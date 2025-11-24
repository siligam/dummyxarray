"""Integration tests for end-to-end workflows."""

import numpy as np

from dummyxarray import DummyDataset


class TestCFComplianceWorkflow:
    """Test complete CF compliance workflow."""

    def test_cf_workflow_from_scratch(self):
        """Test building a CF-compliant dataset from scratch."""
        # Create dataset
        ds = DummyDataset()
        ds.set_global_attrs(Conventions="CF-1.8", title="Test Dataset")

        # Add dimensions
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_dim("lon", 128)

        # Add coordinates
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

        # Infer and set axis attributes
        axes = ds.infer_axis()
        assert axes == {"time": "T", "lat": "Y", "lon": "X"}

        ds.set_axis_attributes()

        # Add variable
        ds.add_variable(
            "temperature",
            dims=["time", "lat", "lon"],
            attrs={"standard_name": "air_temperature", "units": "K"},
        )

        # Validate
        result = ds.validate_cf()
        assert len(result["errors"]) == 0

        # Populate with data
        ds.populate_with_random_data(seed=42)

        # Convert to xarray
        xr_ds = ds.to_xarray()
        assert "temperature" in xr_ds
        assert xr_ds.attrs["Conventions"] == "CF-1.8"


class TestHistoryAndProvenanceWorkflow:
    """Test history and provenance tracking workflow."""

    def test_history_provenance_workflow(self):
        """Test tracking changes through history and provenance."""
        # Create dataset
        ds = DummyDataset()

        # Track initial state
        initial_history_len = len(ds.get_history())

        # Make changes
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temp", dims=["time"])

        # Check history recorded
        history = ds.get_history()
        assert len(history) > initial_history_len

        # Rename and check provenance
        ds.rename_dims(time="t")

        provenance = ds.get_provenance()
        # Provenance is a list of operations with provenance info
        assert len(provenance) > 0
        # Find the rename operation
        rename_ops = [p for p in provenance if p["func"] == "rename_dims"]
        assert len(rename_ops) > 0
        assert "renamed" in rename_ops[0]["provenance"]

        # Reset history
        ds.reset_history()
        # After reset, history contains only __init__
        history_after_reset = ds.get_history()
        assert len(history_after_reset) == 1
        assert history_after_reset[0]["func"] == "__init__"


class TestDataGenerationWorkflow:
    """Test data generation workflow."""

    def test_generate_and_export_workflow(self, tmp_path):
        """Test generating data and exporting to various formats."""
        # Create dataset structure
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 5)
        ds.add_dim("lon", 8)

        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

        ds.add_variable(
            "temperature",
            dims=["time", "lat", "lon"],
            attrs={"units": "K", "standard_name": "air_temperature"},
        )

        # Generate data
        ds.populate_with_random_data(seed=42)

        # Export to YAML
        yaml_path = tmp_path / "dataset.yaml"
        ds.save_yaml(yaml_path)
        assert yaml_path.exists()

        # Export to xarray
        xr_ds = ds.to_xarray()
        assert xr_ds["temperature"].shape == (10, 5, 8)

        # Export to Zarr
        zarr_path = tmp_path / "dataset.zarr"
        ds.to_zarr(zarr_path)
        assert zarr_path.exists()


class TestRenameWorkflow:
    """Test renaming workflow."""

    def test_comprehensive_rename_workflow(self):
        """Test renaming dimensions, coordinates, and variables."""
        # Create dataset
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("latitude", 64)
        ds.add_dim("longitude", 128)

        ds.add_coord("time", dims=["time"])
        ds.add_coord("latitude", dims=["latitude"])
        ds.add_coord("longitude", dims=["longitude"])

        ds.add_variable("temperature", dims=["time", "latitude", "longitude"])

        # Rename using different methods
        ds.rename_dims(latitude="lat", longitude="lon")
        assert "lat" in ds.dims
        assert "lon" in ds.dims
        assert "latitude" not in ds.dims

        # Check coordinates updated
        assert ds.coords["latitude"].dims == ["lat"]
        assert ds.coords["longitude"].dims == ["lon"]

        # Rename variables
        ds.rename_vars(temperature="temp")
        assert "temp" in ds.variables
        assert "temperature" not in ds.variables

        # Use unified rename
        ds.rename(time="t", lat="y", lon="x")
        assert "t" in ds.dims
        assert "y" in ds.dims
        assert "x" in ds.dims


class TestValidationWorkflow:
    """Test validation workflow."""

    def test_validation_and_fix_workflow(self):
        """Test validating and fixing dataset issues."""
        # Create dataset with potential issues
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temp", dims=["time"])

        # Validate CF compliance
        result = ds.validate_cf()
        assert len(result["warnings"]) > 0  # Should have warnings

        # Fix issues
        ds.coords["time"].attrs["units"] = "days since 2000-01-01"
        ds.coords["time"].attrs["standard_name"] = "time"
        ds.coords["time"].attrs["axis"] = "T"

        ds.variables["temp"].attrs["units"] = "K"
        ds.variables["temp"].attrs["standard_name"] = "air_temperature"

        ds.set_global_attrs(Conventions="CF-1.8")

        # Validate again
        result = ds.validate_cf()
        # Should have fewer warnings now
        assert "Conventions" not in str(result["warnings"])


class TestFromXarrayWorkflow:
    """Test importing from xarray workflow."""

    def test_import_modify_export_workflow(self, tmp_path):
        """Test importing from xarray, modifying, and exporting."""
        import xarray as xr

        # Create xarray dataset
        xr_ds = xr.Dataset({"temperature": (["time", "lat", "lon"], np.random.rand(10, 5, 8))})
        xr_ds.attrs["title"] = "Original Dataset"

        # Import to DummyDataset
        ds = DummyDataset.from_xarray(xr_ds)

        # Modify
        ds.set_global_attrs(Conventions="CF-1.8", institution="Test")
        ds.infer_axis()
        ds.set_axis_attributes()

        # Add more variables
        ds.add_variable(
            "pressure",
            dims=["time", "lat", "lon"],
            attrs={"units": "Pa", "standard_name": "air_pressure"},
        )

        # Populate new variable
        ds.populate_with_random_data(seed=42)

        # Export back to xarray
        xr_ds_new = ds.to_xarray()
        assert "pressure" in xr_ds_new
        assert xr_ds_new.attrs["Conventions"] == "CF-1.8"
