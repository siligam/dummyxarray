"""Tests for CF compliance and axis detection features."""

import pytest

from dummyxarray import DummyDataset


class TestResetHistory:
    """Test history reset functionality."""

    def test_reset_history_basic(self):
        """Test basic history reset."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        # Should have 3 operations
        assert len(ds.get_history()) == 3

        # Reset history
        ds.reset_history()

        # Should only have __init__
        assert len(ds.get_history()) == 1
        assert ds.get_history()[0]["func"] == "__init__"

    def test_reset_history_preserves_data(self):
        """Test that reset_history preserves dataset structure."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_coord("time", dims=["time"], attrs={"units": "days"})
        ds.add_variable("temp", dims=["time", "lat"])

        ds.reset_history()

        # Data should still be there
        assert "time" in ds.dims
        assert "lat" in ds.dims
        assert "time" in ds.coords
        assert "temp" in ds.variables
        assert ds.coords["time"].attrs["units"] == "days"

    def test_reset_history_tracks_new_operations(self):
        """Test that operations after reset are tracked."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.reset_history()

        # Add new operations
        ds.add_dim("lat", 64)
        ds.assign_attrs(title="Test")

        history = ds.get_history()
        # Should have __init__, add_dim, assign_attrs
        assert len(history) == 3
        assert history[1]["func"] == "add_dim"
        assert history[2]["func"] == "assign_attrs"


class TestAxisInference:
    """Test axis detection and inference."""

    def test_infer_axis_from_units(self):
        """Test axis inference from units."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_dim("lon", 128)
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

        axes = ds.infer_axis()

        assert axes["time"] == "T"
        assert axes["lat"] == "Y"
        assert axes["lon"] == "X"

    def test_infer_axis_from_names(self):
        """Test axis inference from coordinate names."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"])
        ds.add_coord("latitude", dims=["latitude"])
        ds.add_coord("longitude", dims=["longitude"])
        ds.add_coord("level", dims=["level"])

        axes = ds.infer_axis()

        assert axes["time"] == "T"
        assert axes["latitude"] == "Y"
        assert axes["longitude"] == "X"
        assert axes["level"] == "Z"

    def test_infer_axis_from_standard_name(self):
        """Test axis inference from standard_name."""
        ds = DummyDataset()
        ds.add_coord("x", dims=["x"], attrs={"standard_name": "longitude"})
        ds.add_coord("y", dims=["y"], attrs={"standard_name": "latitude"})
        ds.add_coord("z", dims=["z"], attrs={"standard_name": "height"})
        ds.add_coord("t", dims=["t"], attrs={"standard_name": "time"})

        axes = ds.infer_axis()

        assert axes["x"] == "X"
        assert axes["y"] == "Y"
        assert axes["z"] == "Z"
        assert axes["t"] == "T"

    def test_infer_axis_existing_axis_attr(self):
        """Test that existing axis attributes are preserved."""
        ds = DummyDataset()
        ds.add_coord("custom", dims=["custom"], attrs={"axis": "X"})

        axes = ds.infer_axis()

        assert axes["custom"] == "X"

    def test_infer_axis_specific_coord(self):
        """Test inferring axis for specific coordinate."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})

        # Infer only for time
        axes = ds.infer_axis("time")

        assert "time" in axes
        assert "lat" not in axes
        assert axes["time"] == "T"

    def test_infer_axis_no_match(self):
        """Test axis inference when no pattern matches."""
        ds = DummyDataset()
        ds.add_coord("custom", dims=["custom"])

        axes = ds.infer_axis()

        assert "custom" not in axes


class TestSetAxisAttributes:
    """Test setting axis attributes."""

    def test_set_axis_attributes_basic(self):
        """Test basic axis attribute setting."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})

        assigned = ds.set_axis_attributes()

        assert ds.coords["time"].attrs["axis"] == "T"
        assert ds.coords["lat"].attrs["axis"] == "Y"
        assert assigned == {"time": "T", "lat": "Y"}

    def test_set_axis_attributes_inferred_only(self):
        """Test setting only inferred axes (not overwriting)."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"], attrs={"axis": "X"})  # Wrong but existing
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})

        assigned = ds.set_axis_attributes(inferred_only=True)

        # time should keep its existing (wrong) axis
        assert ds.coords["time"].attrs["axis"] == "X"
        # lat should get inferred axis
        assert ds.coords["lat"].attrs["axis"] == "Y"
        assert "time" not in assigned
        assert assigned["lat"] == "Y"

    def test_set_axis_attributes_overwrite(self):
        """Test overwriting existing axis attributes."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"], attrs={"axis": "X", "units": "days since 2000-01-01"})

        assigned = ds.set_axis_attributes(inferred_only=False)

        # Should overwrite with inferred value
        assert ds.coords["time"].attrs["axis"] == "T"
        assert assigned["time"] == "T"


class TestGetAxisCoordinates:
    """Test getting coordinates by axis."""

    def test_get_axis_coordinates_basic(self):
        """Test getting coordinates by axis type."""
        ds = DummyDataset()
        ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})
        ds.add_coord("lat", dims=["lat"], attrs={"axis": "Y"})
        ds.add_coord("time", dims=["time"], attrs={"axis": "T"})

        x_coords = ds.get_axis_coordinates("X")
        y_coords = ds.get_axis_coordinates("Y")
        t_coords = ds.get_axis_coordinates("T")

        assert x_coords == ["lon"]
        assert y_coords == ["lat"]
        assert t_coords == ["time"]

    def test_get_axis_coordinates_multiple(self):
        """Test getting multiple coordinates with same axis."""
        ds = DummyDataset()
        ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})
        ds.add_coord("x", dims=["x"], attrs={"axis": "X"})

        x_coords = ds.get_axis_coordinates("X")

        assert len(x_coords) == 2
        assert "lon" in x_coords
        assert "x" in x_coords

    def test_get_axis_coordinates_none(self):
        """Test getting coordinates when none match."""
        ds = DummyDataset()
        ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})

        z_coords = ds.get_axis_coordinates("Z")

        assert z_coords == []


class TestCFValidation:
    """Test CF convention validation."""

    def test_validate_cf_missing_axis(self):
        """Test validation catches missing axis attributes."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"])

        result = ds.validate_cf()

        assert len(result["warnings"]) > 0
        assert any("axis" in w.lower() for w in result["warnings"])

    def test_validate_cf_missing_units(self):
        """Test validation catches missing units."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"])
        ds.add_variable("temp", dims=["time"])

        result = ds.validate_cf()

        assert any("units" in w.lower() for w in result["warnings"])

    def test_validate_cf_missing_conventions(self):
        """Test validation catches missing Conventions attribute."""
        ds = DummyDataset()

        result = ds.validate_cf()

        assert any("conventions" in w.lower() for w in result["warnings"])

    def test_validate_cf_missing_standard_name(self):
        """Test validation catches missing standard_name."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"])

        result = ds.validate_cf()

        assert any("standard_name" in w.lower() for w in result["warnings"])

    def test_validate_cf_dimension_order(self):
        """Test validation checks dimension ordering."""
        ds = DummyDataset()
        ds.add_dim("lon", 128)
        ds.add_dim("lat", 64)
        ds.add_dim("time", 10)
        ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})
        ds.add_coord("lat", dims=["lat"], attrs={"axis": "Y"})
        ds.add_coord("time", dims=["time"], attrs={"axis": "T"})
        # Wrong order: X, Y, T instead of T, Y, X
        ds.add_variable("temp", dims=["lon", "lat", "time"])

        result = ds.validate_cf()

        assert any("dimension order" in w.lower() for w in result["warnings"])

    def test_validate_cf_strict_mode(self):
        """Test strict mode raises exception."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"])

        with pytest.raises(ValueError, match="CF validation failed"):
            ds.validate_cf(strict=True)

    def test_validate_cf_compliant_dataset(self):
        """Test validation passes for compliant dataset."""
        ds = DummyDataset()
        ds.assign_attrs(Conventions="CF-1.8")
        ds.add_dim("time", 10)
        ds.add_coord(
            "time",
            dims=["time"],
            attrs={
                "axis": "T",
                "units": "days since 2000-01-01",
                "standard_name": "time",
            },
        )
        ds.add_variable(
            "temp",
            dims=["time"],
            attrs={"units": "K", "standard_name": "air_temperature"},
        )

        result = ds.validate_cf()

        # Should have minimal warnings
        assert len(result["errors"]) == 0


class TestCFWorkflow:
    """Test complete CF compliance workflow."""

    def test_cf_workflow_from_scratch(self):
        """Test building CF-compliant dataset from scratch."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 64)
        ds.add_dim("lon", 128)

        # Add coordinates with units
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

        # Infer and set axis attributes
        ds.set_axis_attributes()

        # Verify axes were set correctly
        assert ds.coords["time"].attrs["axis"] == "T"
        assert ds.coords["lat"].attrs["axis"] == "Y"
        assert ds.coords["lon"].attrs["axis"] == "X"

    def test_cf_workflow_with_reset(self):
        """Test CF workflow with history reset."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"])

        # Reset history after initial setup
        ds.reset_history()

        # Make CF-compliant changes
        ds.coords["time"].attrs["units"] = "days since 2000-01-01"
        ds.set_axis_attributes()
        ds.assign_attrs(Conventions="CF-1.8")

        # History should only show changes after reset
        history = ds.get_history()
        assert len(history) == 2  # __init__ + assign_attrs
        assert history[1]["func"] == "assign_attrs"

    def test_cf_workflow_query_axes(self):
        """Test querying coordinates by axis type."""
        ds = DummyDataset()
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
        ds.add_coord("lev", dims=["lev"], attrs={"units": "hPa"})

        ds.set_axis_attributes()

        # Query by axis type
        assert ds.get_axis_coordinates("T") == ["time"]
        assert ds.get_axis_coordinates("Y") == ["lat"]
        assert ds.get_axis_coordinates("X") == ["lon"]
        assert ds.get_axis_coordinates("Z") == ["lev"]
