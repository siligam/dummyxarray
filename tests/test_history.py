"""Tests for operation history tracking functionality."""

import json
import yaml
import pytest
from dummyxarray import DummyDataset, DummyArray


class TestDummyArrayHistory:
    """Test operation history tracking for DummyArray."""
    
    def test_history_recording_basic(self):
        """Test that operations are recorded in history."""
        arr = DummyArray(dims=["time"])
        arr.assign_attrs(units="K", long_name="Temperature")
        
        history = arr.get_history()
        assert len(history) == 2
        assert history[0]['func'] == '__init__'
        assert history[0]['args']['dims'] == ['time']
        assert history[1]['func'] == 'assign_attrs'
        assert history[1]['args'] == {'units': 'K', 'long_name': 'Temperature'}
    
    def test_history_recording_chaining(self):
        """Test history recording with method chaining."""
        arr = DummyArray(dims=["time"])
        arr.assign_attrs(units="K").assign_attrs(standard_name="air_temperature")
        
        history = arr.get_history()
        assert len(history) == 3
        assert history[1]['func'] == 'assign_attrs'
        assert history[2]['func'] == 'assign_attrs'
    
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
        assert history[0]['func'] == '__init__'
        assert history[1]['func'] == 'add_dim'
        assert history[1]['args'] == {'name': 'time', 'size': 10}
        assert history[2]['func'] == 'add_dim'
        assert history[2]['args'] == {'name': 'lat', 'size': 64}
        assert history[3]['func'] == 'assign_attrs'
        assert history[3]['args'] == {'title': 'Test Dataset'}
    
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
        assert coord_op['func'] == 'add_coord'
        assert coord_op['args']['name'] == 'time'
        assert coord_op['args']['dims'] == ['time']
        assert coord_op['args']['attrs'] == {'units': 'days'}
        
        # Check add_variable
        var_op = history[3]
        assert var_op['func'] == 'add_variable'
        assert var_op['args']['name'] == 'temperature'
        assert var_op['args']['dims'] == ['time']
    
    def test_history_data_placeholder(self):
        """Test that actual data is not stored in history."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        history = ds.get_history()
        coord_op = history[2]
        assert coord_op['args']['data'] == '<data>'  # Placeholder, not actual data
    
    def test_export_history_json(self):
        """Test exporting history as JSON."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")
        
        json_str = ds.export_history('json')
        parsed = json.loads(json_str)
        
        assert len(parsed) == 3
        assert parsed[1]['func'] == 'add_dim'
        assert parsed[2]['func'] == 'assign_attrs'
    
    def test_export_history_yaml(self):
        """Test exporting history as YAML."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")
        
        yaml_str = ds.export_history('yaml')
        parsed = yaml.safe_load(yaml_str)
        
        assert len(parsed) == 3
        assert parsed[1]['func'] == 'add_dim'
    
    def test_export_history_python(self):
        """Test exporting history as Python code."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test Dataset", institution="DKRZ")
        
        python_code = ds.export_history('python')
        
        assert "ds = DummyDataset()" in python_code
        assert "ds.add_dim(name='time', size=10)" in python_code
        assert "ds.assign_attrs(title='Test Dataset', institution='DKRZ')" in python_code
    
    def test_export_history_invalid_format(self):
        """Test that invalid format raises error."""
        ds = DummyDataset()
        
        with pytest.raises(ValueError, match="Unknown format"):
            ds.export_history('invalid')
    
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
        
        json_str = ds.export_history('json')
        new_ds = DummyDataset.replay_history(json_str)
        
        assert new_ds.dims == ds.dims
        assert new_ds.attrs == ds.attrs
    
    def test_replay_history_from_yaml(self):
        """Test replaying history from YAML string."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.assign_attrs(title="Test")
        
        yaml_str = ds.export_history('yaml')
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
        
        ds.add_variable("temperature", 
                       dims=["time", "lat", "lon"],
                       attrs={"units": "K", "long_name": "Temperature"},
                       encoding={"dtype": "float32", "chunks": [6, 32, 64]})
        
        ds.assign_attrs(
            title="Climate Model Output",
            institution="DKRZ",
            experiment="historical"
        )
        
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
        
        python_code = ds.export_history('python')
        
        # Execute the code
        namespace = {'DummyDataset': DummyDataset}
        exec(python_code, namespace)
        
        # Verify the created dataset
        created_ds = namespace['ds']
        assert created_ds.dims == ds.dims
        assert created_ds.attrs == ds.attrs
        assert list(created_ds.coords.keys()) == list(ds.coords.keys())
