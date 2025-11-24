"""Tests for provenance tracking functionality."""

import pytest

from dummyxarray import DummyDataset


class TestProvenance:
    """Test provenance tracking functionality."""

    def test_provenance_assign_attrs_new(self):
        """Test provenance for new attributes."""
        ds = DummyDataset()
        ds.assign_attrs(units="K", title="Test")

        history = ds.get_history()
        prov = history[1]["provenance"]

        assert "modified" in prov
        assert prov["modified"]["units"] == {"before": None, "after": "K"}
        assert prov["modified"]["title"] == {"before": None, "after": "Test"}

    def test_provenance_assign_attrs_overwrite(self):
        """Test provenance for overwriting attributes."""
        ds = DummyDataset()
        ds.assign_attrs(units="degC")
        ds.assign_attrs(units="K")

        history = ds.get_history()
        prov = history[2]["provenance"]

        assert "modified" in prov
        assert prov["modified"]["units"] == {"before": "degC", "after": "K"}

    def test_provenance_add_dim_new(self):
        """Test provenance for adding new dimension."""
        ds = DummyDataset()
        ds.add_dim("time", 10)

        history = ds.get_history()
        prov = history[1]["provenance"]

        assert "added" in prov
        assert "time" in prov["added"]

    def test_provenance_add_dim_modify(self):
        """Test provenance for modifying dimension size."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("time", 20)  # Modify size

        history = ds.get_history()
        prov = history[2]["provenance"]

        assert "modified" in prov
        assert prov["modified"]["time"] == {"before": 10, "after": 20}

    def test_provenance_add_coord_new(self):
        """Test provenance for adding new coordinate."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        history = ds.get_history()
        prov = history[2]["provenance"]

        assert "added" in prov
        assert "time" in prov["added"]

    def test_provenance_add_coord_modify(self):
        """Test provenance for modifying coordinate."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_coord("time", dims=["time"], attrs={"units": "hours"})

        history = ds.get_history()
        prov = history[3]["provenance"]

        assert "modified" in prov
        assert "time" in prov["modified"]
        assert prov["modified"]["time"]["attrs"]["before"] == {"units": "days"}
        assert prov["modified"]["time"]["attrs"]["after"] == {"units": "hours"}

    def test_provenance_add_variable_new(self):
        """Test provenance for adding new variable."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("temp", dims=["time"])

        history = ds.get_history()
        prov = history[2]["provenance"]

        assert "added" in prov
        assert "temp" in prov["added"]

    def test_get_provenance_all(self):
        """Test getting all provenance information."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(units="K")

        prov_list = ds.get_provenance()

        assert len(prov_list) == 2
        assert prov_list[0]["func"] == "add_dim"
        assert prov_list[1]["func"] == "assign_attrs"

    def test_get_provenance_specific(self):
        """Test getting provenance for specific operation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(units="K")

        prov = ds.get_provenance(operation_index=1)

        assert "added" in prov
        assert "time" in prov["added"]

    def test_get_provenance_invalid_index(self):
        """Test that invalid index raises error."""
        ds = DummyDataset()
        ds.add_dim("time", 10)

        with pytest.raises(IndexError):
            ds.get_provenance(operation_index=10)

    def test_visualize_provenance_basic(self):
        """Test basic provenance visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(units="K")

        viz = ds.visualize_provenance()

        assert "Provenance: Dataset Changes" in viz
        assert "Operation 1: add_dim" in viz
        assert "Added: time" in viz
        assert "Operation 2: assign_attrs" in viz
        assert "units: None → 'K'" in viz

    def test_visualize_provenance_compact(self):
        """Test compact provenance visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(units="K")

        viz = ds.visualize_provenance(compact=True)

        assert "1. add_dim: added: time" in viz
        assert "2. assign_attrs: units: None → K" in viz

    def test_visualize_provenance_overwrite(self):
        """Test provenance visualization with overwrites."""
        ds = DummyDataset()
        ds.assign_attrs(units="degC")
        ds.assign_attrs(units="K")

        viz = ds.visualize_provenance()

        assert "units: None → 'degC'" in viz
        assert "units: 'degC' → 'K'" in viz

    def test_get_history_without_provenance(self):
        """Test getting history without provenance information."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(units="K")

        history = ds.get_history(include_provenance=False)

        assert len(history) == 3
        for op in history:
            assert "provenance" not in op
            assert "func" in op
            assert "args" in op

    def test_provenance_complex_workflow(self):
        """Test provenance in a complex workflow."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_variable("temp", dims=["time", "lat"], attrs={"units": "K"})
        ds.assign_attrs(title="Test", institution="DKRZ")
        ds.assign_attrs(title="Updated Test")  # Overwrite title

        prov_list = ds.get_provenance()

        # Check we have provenance for all operations except __init__
        assert len(prov_list) == 6

        # Check the title overwrite
        last_prov = prov_list[-1]["provenance"]
        assert "modified" in last_prov
        assert last_prov["modified"]["title"]["before"] == "Test"
        assert last_prov["modified"]["title"]["after"] == "Updated Test"

    def test_rename_dims_dict(self):
        """Test renaming dimensions with dict."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.rename_dims({"time": "t", "lat": "latitude"})

        assert "t" in ds.dims
        assert "latitude" in ds.dims
        assert "time" not in ds.dims
        assert "lat" not in ds.dims

        history = ds.get_history()
        prov = history[3]["provenance"]

        assert "renamed" in prov
        assert prov["renamed"] == {"time": "t", "lat": "latitude"}

    def test_rename_dims_kwargs(self):
        """Test renaming dimensions with kwargs."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.rename_dims(time="t")

        assert "t" in ds.dims
        assert "time" not in ds.dims

    def test_rename_dims_updates_references(self):
        """Test that renaming dimension updates coord/var references."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temp", dims=["time"])
        ds.rename_dims(time="t")

        assert ds.coords["time"].dims == ["t"]
        assert ds.variables["temp"].dims == ["t"]

    def test_rename_dims_errors(self):
        """Test rename_dims error handling."""
        ds = DummyDataset()
        ds.add_dim("time", 10)

        # Non-existent dimension
        with pytest.raises(KeyError):
            ds.rename_dims(nonexistent="t")

        # Already existing name
        ds.add_dim("lat", 64)
        with pytest.raises(ValueError):
            ds.rename_dims(time="lat")

        # No arguments
        with pytest.raises(ValueError):
            ds.rename_dims()

    def test_rename_vars_dict(self):
        """Test renaming variables with dict."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("temperature", dims=["time"])
        ds.add_variable("pressure", dims=["time"])
        ds.rename_vars({"temperature": "temp", "pressure": "pres"})

        assert "temp" in ds.variables
        assert "pres" in ds.variables
        assert "temperature" not in ds.variables
        assert "pressure" not in ds.variables

    def test_rename_vars_kwargs(self):
        """Test renaming variables with kwargs."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("temperature", dims=["time"])
        ds.rename_vars(temperature="temp")

        assert "temp" in ds.variables
        assert "temperature" not in ds.variables

    def test_rename_combined(self):
        """Test rename() method that handles dims, coords, and vars."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temperature", dims=["time"])

        # Rename dimension, coordinate, and variable at once
        ds.rename({"time": "t", "temperature": "temp"})

        assert "t" in ds.dims
        assert "t" in ds.coords
        assert "temp" in ds.variables
        assert "time" not in ds.dims
        assert "temperature" not in ds.variables

    def test_rename_combined_kwargs(self):
        """Test rename() with kwargs."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("temperature", dims=["time"])
        ds.rename(time="t", temperature="temp")

        assert "t" in ds.dims
        assert "temp" in ds.variables

    def test_visualize_provenance_rename(self):
        """Test provenance visualization with renames."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.rename_dims(time="t")

        viz = ds.visualize_provenance()

        assert "Renamed:" in viz
        assert "time → t" in viz

    def test_visualize_provenance_rename_compact(self):
        """Test compact provenance visualization with renames."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.rename_dims(time="t")

        viz = ds.visualize_provenance(compact=True)

        assert "renamed: time → t" in viz
