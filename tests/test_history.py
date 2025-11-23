"""Tests for operation history tracking functionality."""

import json

import pytest
import yaml

from dummyxarray import DummyArray, DummyDataset


class TestDummyArrayHistory:
    """Test operation history tracking for DummyArray."""

    def test_history_recording_basic(self):
        """Test that operations are recorded in history."""
        arr = DummyArray(dims=["time"])
        arr.assign_attrs(units="K", long_name="Temperature")

        history = arr.get_history()
        assert len(history) == 2
        assert history[0]["func"] == "__init__"
        assert history[0]["args"]["dims"] == ["time"]
        assert history[1]["func"] == "assign_attrs"
        assert history[1]["args"] == {"units": "K", "long_name": "Temperature"}

    def test_history_recording_chaining(self):
        """Test history recording with method chaining."""
        arr = DummyArray(dims=["time"])
        arr.assign_attrs(units="K").assign_attrs(standard_name="air_temperature")

        history = arr.get_history()
        assert len(history) == 3
        assert history[1]["func"] == "assign_attrs"
        assert history[2]["func"] == "assign_attrs"

    def test_history_disabled(self):
        """Test that history can be disabled."""
        arr = DummyArray(dims=["time"], _record_history=False)
        arr.assign_attrs(units="K")

        history = arr.get_history()
        assert history == []

    def test_replay_history(self):
        """Test replaying history to recreate an array."""
        arr = DummyArray(dims=["time"])
        arr.assign_attrs(units="K", long_name="Temperature")
        arr.assign_attrs(standard_name="air_temperature")

        history = arr.get_history()
        new_arr = arr.replay_history(history)

        assert new_arr.dims == arr.dims
        assert new_arr.attrs == arr.attrs
        assert new_arr is not arr  # Different object


class TestDummyDatasetHistory:
    """Test operation history tracking for DummyDataset."""

    def test_history_recording_basic(self):
        """Test that operations are recorded in history."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.assign_attrs(title="Test Dataset")

        history = ds.get_history()
        assert len(history) == 4
        assert history[0]["func"] == "__init__"
        assert history[1]["func"] == "add_dim"
        assert history[1]["args"] == {"name": "time", "size": 10}
        assert history[2]["func"] == "add_dim"
        assert history[2]["args"] == {"name": "lat", "size": 64}
        assert history[3]["func"] == "assign_attrs"
        assert history[3]["args"] == {"title": "Test Dataset"}

    def test_history_with_coords_and_vars(self):
        """Test history recording with coordinates and variables."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_variable("temperature", dims=["time"], attrs={"units": "K"})

        history = ds.get_history()
        assert len(history) == 4

        # Check add_coord
        coord_op = history[2]
        assert coord_op["func"] == "add_coord"
        assert coord_op["args"]["name"] == "time"
        assert coord_op["args"]["dims"] == ["time"]
        assert coord_op["args"]["attrs"] == {"units": "days"}

        # Check add_variable
        var_op = history[3]
        assert var_op["func"] == "add_variable"
        assert var_op["args"]["name"] == "temperature"
        assert var_op["args"]["dims"] == ["time"]

    def test_history_data_placeholder(self):
        """Test that actual data is not stored in history."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        history = ds.get_history()
        coord_op = history[2]
        assert coord_op["args"]["data"] == "<data>"  # Placeholder, not actual data

    def test_export_history_json(self):
        """Test exporting history as JSON."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        json_str = ds.export_history("json")
        parsed = json.loads(json_str)

        assert len(parsed) == 3
        assert parsed[1]["func"] == "add_dim"
        assert parsed[2]["func"] == "assign_attrs"

    def test_export_history_yaml(self):
        """Test exporting history as YAML."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        yaml_str = ds.export_history("yaml")
        parsed = yaml.safe_load(yaml_str)

        assert len(parsed) == 3
        assert parsed[1]["func"] == "add_dim"

    def test_export_history_python(self):
        """Test exporting history as Python code."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test Dataset", institution="DKRZ")

        python_code = ds.export_history("python")

        assert "ds = DummyDataset()" in python_code
        assert "ds.add_dim(name='time', size=10)" in python_code
        assert "ds.assign_attrs(title='Test Dataset', institution='DKRZ')" in python_code

    def test_export_history_invalid_format(self):
        """Test that invalid format raises error."""
        ds = DummyDataset()

        with pytest.raises(ValueError, match="Unknown format"):
            ds.export_history("invalid")

    def test_replay_history(self):
        """Test replaying history to recreate a dataset."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_variable("temperature", dims=["time", "lat"], attrs={"units": "K"})
        ds.assign_attrs(title="Test Dataset")

        history = ds.get_history()
        new_ds = DummyDataset.replay_history(history)

        assert new_ds.dims == ds.dims
        assert new_ds.attrs == ds.attrs
        assert list(new_ds.coords.keys()) == list(ds.coords.keys())
        assert list(new_ds.variables.keys()) == list(ds.variables.keys())
        assert new_ds is not ds  # Different object

    def test_replay_history_from_json(self):
        """Test replaying history from JSON string."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        json_str = ds.export_history("json")
        new_ds = DummyDataset.replay_history(json_str)

        assert new_ds.dims == ds.dims
        assert new_ds.attrs == ds.attrs

    def test_replay_history_from_yaml(self):
        """Test replaying history from YAML string."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        yaml_str = ds.export_history("yaml")
        new_ds = DummyDataset.replay_history(yaml_str)

        assert new_ds.dims == ds.dims
        assert new_ds.attrs == ds.attrs

    def test_history_disabled(self):
        """Test that history can be disabled."""
        ds = DummyDataset(_record_history=False)
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        history = ds.get_history()
        assert history == []

    def test_complex_workflow(self):
        """Test a complex workflow with history."""
        ds = DummyDataset()
        ds.add_dim("time", 12)
        ds.add_dim("lat", 180)
        ds.add_dim("lon", 360)

        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

        ds.add_variable(
            "temperature",
            dims=["time", "lat", "lon"],
            attrs={"units": "K", "long_name": "Temperature"},
            encoding={"dtype": "float32", "chunks": [6, 32, 64]},
        )

        ds.assign_attrs(title="Climate Model Output", institution="DKRZ", experiment="historical")

        # Export and replay
        history = ds.get_history()
        new_ds = DummyDataset.replay_history(history)

        # Verify structure
        assert new_ds.dims == ds.dims
        assert new_ds.attrs == ds.attrs
        assert set(new_ds.coords.keys()) == set(ds.coords.keys())
        assert set(new_ds.variables.keys()) == set(ds.variables.keys())

        # Verify coordinate attributes
        assert new_ds.coords["time"].attrs == ds.coords["time"].attrs

        # Verify variable attributes and encoding
        assert new_ds.variables["temperature"].attrs == ds.variables["temperature"].attrs
        assert new_ds.variables["temperature"].encoding == ds.variables["temperature"].encoding

    def test_python_code_execution(self):
        """Test that exported Python code can be executed."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.assign_attrs(title="Test")

        python_code = ds.export_history("python")

        # Execute the code
        namespace = {"DummyDataset": DummyDataset}
        exec(python_code, namespace)

        # Verify the created dataset
        created_ds = namespace["ds"]
        assert created_ds.dims == ds.dims
        assert created_ds.attrs == ds.attrs
        assert list(created_ds.coords.keys()) == list(ds.coords.keys())


class TestHistoryVisualization:
    """Test history visualization functionality."""

    def test_visualize_text_basic(self):
        """Test basic text visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")

        viz = ds.visualize_history(format="text")

        assert "Dataset Construction History" in viz
        assert "__init__()" in viz
        assert "add_dim" in viz
        assert "assign_attrs" in viz
        assert "Summary:" in viz
        assert "Total operations: 3" in viz

    def test_visualize_text_compact(self):
        """Test compact text visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)

        viz = ds.visualize_history(format="text", compact=True)

        assert "Dataset Construction History" not in viz
        assert "Summary:" not in viz
        assert "1. __init__()" in viz
        assert "2. add_dim" in viz
        assert "3. add_dim" in viz

    def test_visualize_text_no_args(self):
        """Test text visualization without arguments."""
        ds = DummyDataset()
        ds.add_dim("time", 10)

        viz = ds.visualize_history(format="text", show_args=False)

        assert "add_dim()" in viz
        assert "name=" not in viz
        assert "size=" not in viz

    def test_visualize_dot(self):
        """Test DOT format visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        viz = ds.visualize_history(format="dot")

        assert "digraph dataset_history" in viz
        assert "rankdir=TB" in viz
        assert "op0" in viz
        assert "op1" in viz
        assert "op2" in viz
        assert "->" in viz
        assert "fillcolor=" in viz

    def test_visualize_dot_colors(self):
        """Test that DOT visualization uses different colors for operations."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temp", dims=["time"])

        viz = ds.visualize_history(format="dot")

        # Check that different colors are used
        assert "lightblue" in viz  # __init__
        assert "lightgreen" in viz  # add_dim
        assert "lightyellow" in viz  # add_coord
        assert "lightcoral" in viz  # add_variable

    def test_visualize_mermaid(self):
        """Test Mermaid format visualization."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        viz = ds.visualize_history(format="mermaid")

        assert "graph TD" in viz
        assert "op0" in viz
        assert "op1" in viz
        assert "op2" in viz
        assert "-->" in viz

    def test_visualize_mermaid_shapes(self):
        """Test that Mermaid uses different shapes for different operations."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        viz = ds.visualize_history(format="mermaid")

        # __init__ uses square brackets
        assert 'op0["__init__"]' in viz
        # add_dim uses parentheses (rounded)
        assert 'op1("add_dim' in viz

    def test_visualize_empty_history(self):
        """Test visualization with no history."""
        ds = DummyDataset(_record_history=False)

        viz = ds.visualize_history(format="text")
        assert viz == "No operations recorded"

    def test_visualize_invalid_format(self):
        """Test that invalid format raises error."""
        ds = DummyDataset()

        with pytest.raises(ValueError, match="Unknown format"):
            ds.visualize_history(format="invalid")

    def test_visualize_complex_workflow(self):
        """Test visualization of a complex workflow."""
        ds = DummyDataset()
        ds.add_dim("time", 12)
        ds.add_dim("lat", 180)
        ds.add_dim("lon", 360)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
        ds.add_variable("temperature", dims=["time", "lat", "lon"], attrs={"units": "K"})
        ds.assign_attrs(title="Climate Data", institution="DKRZ")

        viz = ds.visualize_history(format="text")

        assert "Total operations: 9" in viz
        assert "add_dim: 3" in viz
        assert "add_coord: 3" in viz
        assert "add_variable: 1" in viz
        assert "assign_attrs: 1" in viz

    def test_visualize_operation_breakdown(self):
        """Test that operation breakdown is correct."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_dim("lon", 128)
        ds.assign_attrs(title="Test")
        ds.assign_attrs(institution="DKRZ")

        viz = ds.visualize_history(format="text")

        assert "add_dim: 3" in viz
        assert "assign_attrs: 2" in viz


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
