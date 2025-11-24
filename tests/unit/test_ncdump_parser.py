"""Tests for ncdump header parser."""

import pytest

from dummyxarray import from_ncdump_header
from dummyxarray.ncdump_parser import (
    _parse_attribute_value,
    _parse_dimensions,
    _parse_global_attributes,
    _parse_variables,
    parse_ncdump_header,
)


@pytest.fixture
def simple_ncdump_header():
    """Simple ncdump header for testing."""
    return """
netcdf example {
dimensions:
	time = 12 ;
	lat = 64 ;
	lon = 128 ;
variables:
	double time(time) ;
		time:units = "days since 2000-01-01" ;
		time:calendar = "gregorian" ;
	double lat(lat) ;
		lat:units = "degrees_north" ;
		lat:standard_name = "latitude" ;
	double lon(lon) ;
		lon:units = "degrees_east" ;
		lon:standard_name = "longitude" ;
	float temperature(time, lat, lon) ;
		temperature:units = "K" ;
		temperature:standard_name = "air_temperature" ;
		temperature:long_name = "Air Temperature" ;

// global attributes:
		:Conventions = "CF-1.8" ;
		:title = "Example Climate Data" ;
		:institution = "DKRZ" ;
}
"""


@pytest.fixture
def unlimited_dim_header():
    """Header with UNLIMITED dimension."""
    return """
netcdf example {
dimensions:
	time = UNLIMITED ; // (365 currently)
	lat = 64 ;
variables:
	double time(time) ;
		time:units = "days since 2000-01-01" ;
}
"""


class TestParseDimensions:
    """Test dimension parsing."""

    def test_parse_simple_dimensions(self):
        """Test parsing simple dimensions."""
        dims_text = """
        time = 12 ;
        lat = 64 ;
        lon = 128 ;
        """
        dims = _parse_dimensions(dims_text)
        assert dims == {"time": 12, "lat": 64, "lon": 128}

    def test_parse_unlimited_dimension(self):
        """Test parsing UNLIMITED dimension."""
        dims_text = "time = UNLIMITED ; // (365 currently)"
        dims = _parse_dimensions(dims_text)
        assert dims == {"time": 365}

    def test_parse_unlimited_without_current(self):
        """Test UNLIMITED without current size."""
        dims_text = "time = UNLIMITED ;"
        dims = _parse_dimensions(dims_text)
        assert dims == {"time": None}


class TestParseVariables:
    """Test variable parsing."""

    def test_parse_coordinate_variable(self):
        """Test parsing coordinate variable."""
        vars_text = """
        double time(time) ;
            time:units = "days since 2000-01-01" ;
            time:calendar = "gregorian" ;
        """
        variables = _parse_variables(vars_text)

        assert "time" in variables
        assert variables["time"]["dims"] == ["time"]
        assert variables["time"]["dtype"] == "double"
        assert variables["time"]["attrs"]["units"] == "days since 2000-01-01"
        assert variables["time"]["attrs"]["calendar"] == "gregorian"

    def test_parse_multidim_variable(self):
        """Test parsing multi-dimensional variable."""
        vars_text = """
        float temperature(time, lat, lon) ;
            temperature:units = "K" ;
            temperature:standard_name = "air_temperature" ;
        """
        variables = _parse_variables(vars_text)

        assert "temperature" in variables
        assert variables["temperature"]["dims"] == ["time", "lat", "lon"]
        assert variables["temperature"]["dtype"] == "float"
        assert variables["temperature"]["attrs"]["units"] == "K"


class TestParseGlobalAttributes:
    """Test global attribute parsing."""

    def test_parse_global_attributes(self):
        """Test parsing global attributes."""
        header = """
// global attributes:
        :Conventions = "CF-1.8" ;
        :title = "Example Data" ;
        :version = 1 ;
}
"""
        attrs = _parse_global_attributes(header)

        assert attrs["Conventions"] == "CF-1.8"
        assert attrs["title"] == "Example Data"
        assert attrs["version"] == 1


class TestParseAttributeValue:
    """Test attribute value parsing."""

    def test_parse_string_value(self):
        """Test parsing quoted string."""
        assert _parse_attribute_value('"CF-1.8"') == "CF-1.8"
        assert _parse_attribute_value('"days since 2000-01-01"') == "days since 2000-01-01"

    def test_parse_integer_value(self):
        """Test parsing integer."""
        assert _parse_attribute_value("42") == 42
        assert _parse_attribute_value("0") == 0

    def test_parse_float_value(self):
        """Test parsing float."""
        assert _parse_attribute_value("3.14") == 3.14
        assert _parse_attribute_value("1.5e-3") == 1.5e-3

    def test_parse_array_value(self):
        """Test parsing array."""
        result = _parse_attribute_value("1.0, 2.0, 3.0")
        assert result == [1.0, 2.0, 3.0]


class TestParseNcdumpHeader:
    """Test full header parsing."""

    def test_parse_complete_header(self, simple_ncdump_header):
        """Test parsing complete header."""
        metadata = parse_ncdump_header(simple_ncdump_header)

        # Check dimensions
        assert metadata["dimensions"] == {"time": 12, "lat": 64, "lon": 128}

        # Check variables
        assert "time" in metadata["variables"]
        assert "temperature" in metadata["variables"]
        assert metadata["variables"]["temperature"]["dims"] == ["time", "lat", "lon"]

        # Check global attributes
        assert metadata["global_attrs"]["Conventions"] == "CF-1.8"
        assert metadata["global_attrs"]["title"] == "Example Climate Data"


class TestFromNcdumpHeader:
    """Test DummyDataset creation from ncdump header."""

    def test_create_dataset_from_header(self, simple_ncdump_header):
        """Test creating DummyDataset from header."""
        ds = from_ncdump_header(simple_ncdump_header)

        # Check dimensions
        assert ds.dims == {"time": 12, "lat": 64, "lon": 128}

        # Check coordinates
        assert "time" in ds.coords
        assert "lat" in ds.coords
        assert "lon" in ds.coords
        assert ds.coords["time"].attrs["units"] == "days since 2000-01-01"

        # Check variables
        assert "temperature" in ds.variables
        assert ds.variables["temperature"].dims == ["time", "lat", "lon"]
        assert ds.variables["temperature"].attrs["standard_name"] == "air_temperature"

        # Check global attributes
        assert ds.attrs["Conventions"] == "CF-1.8"
        assert ds.attrs["title"] == "Example Climate Data"

    def test_coordinate_detection(self, simple_ncdump_header):
        """Test that coordinates are correctly identified."""
        ds = from_ncdump_header(simple_ncdump_header)

        # Variables with same name as their only dimension should be coordinates
        assert "time" in ds.coords
        assert "lat" in ds.coords
        assert "lon" in ds.coords

        # Multi-dimensional variables should not be coordinates
        assert "temperature" not in ds.coords
        assert "temperature" in ds.variables

    def test_unlimited_dimension(self, unlimited_dim_header):
        """Test handling of UNLIMITED dimensions."""
        ds = from_ncdump_header(unlimited_dim_header)

        # Should use the current size from comment
        assert ds.dims["time"] == 365

    def test_history_recording(self, simple_ncdump_header):
        """Test that history is recorded by default."""
        ds = from_ncdump_header(simple_ncdump_header, record_history=True)

        history = ds.get_history()
        assert len(history) > 0

        # Should have operations for dims, coords, variables, attrs
        func_names = [op["func"] for op in history]
        assert "add_dim" in func_names
        assert "add_coord" in func_names
        assert "add_variable" in func_names

    def test_no_history_recording(self, simple_ncdump_header):
        """Test disabling history recording."""
        ds = from_ncdump_header(simple_ncdump_header, record_history=False)

        # History should be empty or None when disabled
        history = ds.get_history()
        assert history is None or len(history) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_header(self):
        """Test parsing empty header."""
        header = "netcdf empty { }"
        metadata = parse_ncdump_header(header)

        assert metadata["dimensions"] == {}
        assert metadata["variables"] == {}
        assert metadata["global_attrs"] == {}

    def test_no_global_attributes(self):
        """Test header without global attributes."""
        header = """
netcdf example {
dimensions:
    time = 10 ;
variables:
    double time(time) ;
}
"""
        ds = from_ncdump_header(header)
        assert ds.attrs == {}

    def test_variable_without_attributes(self):
        """Test variable without attributes."""
        header = """
netcdf example {
dimensions:
    time = 10 ;
variables:
    double time(time) ;
}
"""
        ds = from_ncdump_header(header)
        assert "time" in ds.coords
        assert ds.coords["time"].attrs == {}
