"""
Tests for STAC functionality in dummyxarray.

This module tests the STAC (SpatioTemporal Asset Catalog) support including
item/collection conversion, spatial/temporal extent detection, and validation.
"""

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from dummyxarray import DummyDataset


def has_stac():
    """Check if STAC dependencies are available."""
    try:
        import pystac  # noqa: F401

        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not has_stac(),
    reason="STAC dependencies not installed. Install with: pip install 'dummyxarray[stac]'",
)


class TestSTACBasics:
    """Test basic STAC functionality."""

    def test_dataset_to_stac_item_basic(self, dataset_with_coords):
        """Test basic dataset to STAC Item conversion."""
        # Add some attributes
        dataset_with_coords.attrs.update(
            {"title": "Test Dataset", "description": "A test dataset for STAC", "license": "MIT"}
        )

        # Create STAC Item
        item = dataset_with_coords.to_stac_item(
            id="test-item", properties={"test_prop": "test_value"}
        )

        # Verify basic properties
        assert item.id == "test-item"
        assert item.properties["test_prop"] == "test_value"
        assert item.properties["title"] == "Test Dataset"
        assert item.properties["description"] == "A test dataset for STAC"
        assert item.properties["license"] == "MIT"

    def test_stac_item_to_dataset_basic(self, dataset_with_coords):
        """Test basic STAC Item to dataset conversion."""
        import pystac

        # Create a STAC Item
        item = pystac.Item(
            id="test-item",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0], [-10.0, -10.0]]
                ],
            },
            bbox=[-10.0, -10.0, 10.0, 10.0],
            datetime=datetime(2020, 1, 1),
            properties={"title": "Test Item", "description": "A test STAC item"},
        )

        # Convert to dataset
        ds = DummyDataset.from_stac_item(item)

        # Verify basic properties
        assert ds.attrs["stac_id"] == "test-item"
        assert ds.attrs["stac_type"] == "Feature"
        assert ds.attrs["title"] == "Test Item"
        assert ds.attrs["description"] == "A test STAC item"
        assert "geospatial_bounds" in ds.attrs
        assert "time_coverage_start" in ds.attrs
        assert "time_coverage_end" in ds.attrs

    def test_stac_roundtrip(self, dataset_with_coords):
        """Test round-trip conversion between dataset and STAC Item."""
        # Add some test data
        dataset_with_coords.add_variable(
            "temperature",
            ["time", "lat", "lon"],
            attrs={"units": "K", "standard_name": "air_temperature"},
        )
        dataset_with_coords.attrs["title"] = "Roundtrip Test"

        # Convert to STAC Item and back
        item = dataset_with_coords.to_stac_item(id="roundtrip-test")
        new_ds = DummyDataset.from_stac_item(item)

        # Verify basic structure
        assert "temperature" in new_ds.variables
        assert new_ds.attrs["title"] == "Roundtrip Test"
        assert new_ds.attrs["stac_id"] == "roundtrip-test"


class TestSTACExtent:
    """Test spatial and temporal extent detection."""

    def test_bbox_from_geospatial_bounds(self):
        """Test bbox extraction from geospatial_bounds attribute."""
        ds = DummyDataset()
        ds.attrs["geospatial_bounds"] = {
            "type": "Polygon",
            "coordinates": [
                [[-120.0, 30.0], [-110.0, 30.0], [-110.0, 40.0], [-120.0, 40.0], [-120.0, 30.0]]
            ],
        }

        item = ds.to_stac_item(id="test-bbox")
        assert item.bbox == [-120.0, 30.0, -110.0, 40.0]

    def test_bbox_from_coordinates(self):
        """Test bbox extraction from coordinate data."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("lat", 5)
        ds.add_dim("lon", 10)
        ds.add_coord("lat", ["lat"], data=np.linspace(-45, 45, 5))
        ds.add_coord("lon", ["lon"], data=np.linspace(-90, 90, 10))

        item = ds.to_stac_item(id="test-coords")

        # Check that bbox was created from coordinates
        assert item.bbox is not None
        assert len(item.bbox) == 4
        assert item.bbox[0] == -90.0  # min lon
        assert item.bbox[1] == -45.0  # min lat
        assert item.bbox[2] == 90.0  # max lon
        assert item.bbox[3] == 45.0  # max lat

    def test_temporal_extent_inference(self):
        """Test temporal extent inference from time coordinate."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("time", 5)
        ds.add_coord("time", ["time"], data=np.arange(5), attrs={"units": "days since 2000-01-01"})

        # Infer temporal extent
        start, end = ds.infer_temporal_extent()

        assert start is not None
        assert end is not None
        assert "time_coverage_start" in ds.attrs
        assert "time_coverage_end" in ds.attrs


class TestSTACCollections:
    """Test STAC Collection functionality."""

    def test_dataset_to_stac_collection(self, dataset_with_coords):
        """Test dataset to STAC Collection conversion."""
        collection = dataset_with_coords.to_stac_collection(
            id="test-collection", description="A test collection", license="Apache-2.0"
        )

        # Verify basic properties
        assert collection.id == "test-collection"
        assert collection.description == "A test collection"
        assert collection.license == "Apache-2.0"
        assert collection.extent is not None

        # Should have one item
        items = list(collection.get_all_items())
        assert len(items) == 1
        assert items[0].id == "test-collection-item"

    def test_stac_collection_to_dataset(self, dataset_with_coords):
        """Test STAC Collection to dataset conversion."""
        import pystac

        # Create a collection
        collection = pystac.Collection(
            id="test-collection",
            description="Test collection",
            extent=pystac.Extent(
                spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
                temporal=pystac.TemporalExtent([["2020-01-01T00:00:00Z", "2020-12-31T23:59:59Z"]]),
            ),
        )

        # Add an item
        item = dataset_with_coords.to_stac_item(id="collection-item")
        collection.add_item(item)

        # Convert back to dataset
        ds = DummyDataset.from_stac_collection(collection, item_id="collection-item")

        assert ds.attrs["stac_id"] == "collection-item"

    def test_create_collection_from_datasets(self):
        """Test creating collection from multiple datasets."""
        import numpy as np

        # Create multiple datasets
        datasets = []
        for i in range(3):
            ds = DummyDataset()
            ds.add_dim("lat", 5)
            ds.add_dim("lon", 5)
            ds.add_coord("lat", ["lat"], data=np.linspace(-10 + i * 10, 10 + i * 10, 5))
            ds.add_coord("lon", ["lon"], data=np.linspace(-10 + i * 10, 10 + i * 10, 5))
            ds.attrs[f"dataset_{i}"] = True
            datasets.append(ds)

        # Create collection
        collection = DummyDataset.create_stac_collection(
            datasets,
            collection_id="multi-dataset-collection",
            description="Collection with multiple datasets",
        )

        # Verify collection
        assert collection.id == "multi-dataset-collection"
        assert collection.description == "Collection with multiple datasets"

        # Should have 3 items
        items = list(collection.get_all_items())
        assert len(items) == 3

        # Extent should cover all datasets
        assert collection.extent is not None
        assert collection.extent.spatial is not None
        assert len(collection.extent.spatial.bboxes) == 1


class TestSTACSpatial:
    """Test spatial functionality."""

    def test_add_spatial_extent(self):
        """Test adding spatial extent to dataset."""
        ds = DummyDataset()
        ds.add_spatial_extent(lat_bounds=(-45, 45), lon_bounds=(-90, 90))

        # Verify attributes
        assert ds.attrs["geospatial_lat_min"] == -45
        assert ds.attrs["geospatial_lat_max"] == 45
        assert ds.attrs["geospatial_lon_min"] == -90
        assert ds.attrs["geospatial_lon_max"] == 90

        # Verify geospatial_bounds structure
        bounds = ds.attrs["geospatial_bounds"]
        assert bounds["type"] == "Polygon"
        assert len(bounds["coordinates"]) == 1
        assert len(bounds["coordinates"][0]) == 5  # 5 vertices for closed polygon

    def test_validate_spatial_metadata_valid(self):
        """Test spatial metadata validation with valid data."""
        ds = DummyDataset()
        ds.add_spatial_extent(lat_bounds=(-45, 45), lon_bounds=(-90, 90))

        validation = ds.validate_spatial_metadata()
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0

    def test_validate_spatial_metadata_invalid(self):
        """Test spatial metadata validation with invalid data."""
        ds = DummyDataset()
        ds.attrs["geospatial_bounds"] = "invalid"

        validation = ds.validate_spatial_metadata()
        assert validation["valid"] is False
        assert len(validation["issues"]) > 0
        assert any("must be a dictionary" in issue for issue in validation["issues"])

    def test_validate_spatial_metadata_missing(self):
        """Test spatial metadata validation with missing data."""
        ds = DummyDataset()
        # No spatial information added

        validation = ds.validate_spatial_metadata()
        assert validation["valid"] is False
        assert len(validation["issues"]) > 0
        assert any("No spatial information found" in issue for issue in validation["issues"])


class TestSTACFileIO:
    """Test STAC file I/O operations."""

    def test_save_load_stac_item(self, dataset_with_coords, tmp_path):
        """Test saving and loading STAC Item to/from file."""
        import pystac

        dataset_with_coords.attrs["title"] = "File I/O Test"

        # Create STAC Item
        item = dataset_with_coords.to_stac_item(id="file-test-item")

        # Save to file
        item_path = tmp_path / "test_item.json"
        item.save_object(dest_href=str(item_path))

        # Load from file
        loaded_item = pystac.Item.from_file(str(item_path))

        # Convert back to dataset
        loaded_ds = DummyDataset.from_stac_item(loaded_item)

        # Verify metadata preservation
        assert loaded_ds.attrs["title"] == "File I/O Test"
        assert loaded_ds.attrs["stac_id"] == "file-test-item"

    def test_save_load_stac_collection(self, dataset_with_coords, tmp_path):
        """Test saving and loading STAC Collection to/from file."""
        import pystac

        # Create STAC Collection
        collection = dataset_with_coords.to_stac_collection(
            id="file-test-collection", description="File I/O test collection"
        )

        # Save to file
        collection_path = tmp_path / "test_collection.json"
        collection.save_object(dest_href=str(collection_path))

        # Load from file
        loaded_collection = pystac.Collection.from_file(str(collection_path))

        # Convert back to dataset - single-file collections return collection metadata
        loaded_ds = DummyDataset.from_stac_collection(loaded_collection)

        # Verify metadata preservation
        assert loaded_ds.attrs["stac_id"] == "file-test-collection"


class TestSTACErrorHandling:
    """Test STAC error handling."""

    def test_stac_collection_item_not_found(self):
        """Test error when item not found in collection."""
        import pystac
        from pystac import Extent, SpatialExtent, TemporalExtent

        collection = pystac.Collection(
            id="test-collection",
            description="Test collection",
            extent=Extent(
                spatial=SpatialExtent([[-180, -90, 180, 90]]),
                temporal=TemporalExtent([[None, None]]),
            ),
        )

        with pytest.raises(Exception):  # Should raise STACError
            DummyDataset.from_stac_collection(collection, item_id="nonexistent-item")

    def test_create_collection_empty_datasets(self):
        """Test error when creating collection with no datasets."""
        with pytest.raises(Exception):  # Should raise STACError
            DummyDataset.create_stac_collection([], collection_id="empty-collection")


class TestSTACEnhancedBbox:
    """Test enhanced bbox extraction functionality."""

    def test_bbox_prefer_geospatial_bounds(self):
        """Test that geospatial_bounds takes precedence over coordinates."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("lat", 5)
        ds.add_dim("lon", 10)
        ds.add_coord("lat", ["lat"], data=np.linspace(-45, 45, 5))
        ds.add_coord("lon", ["lon"], data=np.linspace(-90, 90, 10))

        # Add geospatial bounds (should take precedence)
        ds.attrs["geospatial_bounds"] = {
            "type": "Polygon",
            "coordinates": [
                [[-100.0, 20.0], [-80.0, 20.0], [-80.0, 30.0], [-100.0, 30.0], [-100.0, 20.0]]
            ],
        }

        item = ds.to_stac_item(id="test-precedence")

        # Should use geospatial_bounds, not coordinates
        assert item.bbox == [-100.0, 20.0, -80.0, 30.0]

    def test_bbox_fallback_to_coordinates(self):
        """Test bbox extraction falls back to coordinates when no geospatial_bounds."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("lat", 3)
        ds.add_dim("lon", 4)
        ds.add_coord("lat", ["lat"], data=np.array([-10, 0, 10]))
        ds.add_coord("lon", ["lon"], data=np.array([-20, 0, 20, 40]))

        # No geospatial_bounds - should use coordinates
        item = ds.to_stac_item(id="test-fallback")

        # Should derive from coordinate data
        assert item.bbox == [-20.0, -10.0, 40.0, 10.0]

    def test_bbox_no_spatial_data(self):
        """Test bbox extraction with no spatial data."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", ["time"], data=np.arange(10))

        # No spatial information
        item = ds.to_stac_item(id="test-no-spatial")

        # Should return None for bbox
        assert item.bbox is None

    def test_bbox_alternative_coordinate_names(self):
        """Test bbox extraction with alternative coordinate names."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("latitude", 3)
        ds.add_dim("longitude", 4)
        ds.add_coord("latitude", ["latitude"], data=np.array([-10, 0, 10]))
        ds.add_coord("longitude", ["longitude"], data=np.array([-20, 0, 20, 40]))

        # Use alternative coordinate names
        item = ds.to_stac_item(id="test-alt-names")

        # Should find alternative coordinate names
        assert item.bbox == [-20.0, -10.0, 40.0, 10.0]

    def test_bbox_partial_coordinates(self):
        """Test bbox extraction with only lat or only lon coordinates."""
        import numpy as np

        ds = DummyDataset()
        ds.add_coord("lat", ["lat"], data=np.array([-10, 0, 10]))
        # Missing lon coordinates

        item = ds.to_stac_item(id="test-partial")

        # Should return None when missing either lat or lon
        assert item.bbox is None


class TestSTACTemporalExtent:
    """Test temporal extent functionality."""

    def test_infer_temporal_extent_with_units(self):
        """Test temporal extent inference with proper units."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("time", 5)
        ds.add_coord(
            "time",
            ["time"],
            data=np.array([0, 1, 2, 3, 4]),
            attrs={"units": "days since 2000-01-01"},
        )

        start, end = ds.infer_temporal_extent()

        assert start is not None
        assert end is not None
        assert start.year == 2000
        assert start.month == 1
        assert start.day == 1
        assert end.year == 2000
        assert end.month == 1
        assert end.day == 5

    def test_infer_temporal_extent_no_time_coord(self):
        """Test temporal extent inference with no time coordinate."""
        ds = DummyDataset()
        ds.add_dim("lat", 5)
        ds.add_dim("lon", 10)

        start, end = ds.infer_temporal_extent()

        # Should return None when no time coordinate
        assert start is None
        assert end is None

    def test_infer_temporal_extent_invalid_units(self):
        """Test temporal extent inference with invalid units."""
        import numpy as np

        ds = DummyDataset()
        ds.add_dim("time", 5)
        ds.add_coord(
            "time",
            ["time"],
            data=np.array([0, 1, 2, 3, 4]),
            attrs={"units": "invalid units"},  # No "since" keyword
        )

        start, end = ds.infer_temporal_extent()

        # Should return None for invalid units
        assert start is None
        assert end is None


class TestSTACIntegration:
    """Test STAC integration with other dummyxarray features."""

    def test_stac_with_data_generation(self, dataset_with_coords):
        """Test STAC with data generation features."""
        dataset_with_coords.add_variable(
            "temperature",
            ["time", "lat", "lon"],
            attrs={"units": "K"},
        )

        # Populate with random data
        dataset_with_coords.populate_with_random_data(seed=42)

        # Convert to STAC
        item = dataset_with_coords.to_stac_item(id="data-gen-test")

        # Verify that variable metadata is preserved
        assert "variables" in item.properties
        assert len(item.properties["variables"]) > 0

    def test_stac_with_cf_compliance(self, dataset_with_coords):
        """Test STAC with CF compliance features."""
        # Add CF-compliant metadata
        dataset_with_coords.add_variable(
            "temperature",
            ["time", "lat", "lon"],
            attrs={
                "units": "K",
                "standard_name": "air_temperature",
                "long_name": "Air Temperature",
            },
        )

        # Convert to STAC
        item = dataset_with_coords.to_stac_item(id="cf-test")

        # Verify CF metadata is preserved in item properties
        assert "var_temperature" in item.properties
        assert item.properties["var_temperature"]["units"] == "K"
        assert item.properties["var_temperature"]["standard_name"] == "air_temperature"
