"""Tests for validation functionality (ValidationMixin)."""

import numpy as np
import pytest

from dummyxarray import DummyArray, DummyDataset


class TestDatasetValidation:
    """Test dataset validation functionality."""

    def test_validate_empty_dataset(self, empty_dataset):
        """Test validating an empty dataset."""
        # Should not raise
        empty_dataset.validate()

    def test_validate_simple_dataset(self, simple_dataset):
        """Test validating a simple dataset with dimensions."""
        # Should not raise
        simple_dataset.validate()

    def test_validate_with_coords(self, dataset_with_coords):
        """Test validating dataset with coordinates."""
        # Should not raise
        dataset_with_coords.validate()

    def test_validate_unknown_dimension(self):
        """Test validation fails for unknown dimensions."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("temp", dims=["unknown_dim"])

        with pytest.raises(ValueError, match="Unknown dimension"):
            ds.validate()

    def test_validate_shape_mismatch(self):
        """Test validation fails when data shape doesn't match dims."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 5)

        # Add coordinate with wrong shape - this will raise during add_coord
        # because _infer_and_register_dims checks for conflicts
        with pytest.raises(ValueError, match="Dimension mismatch"):
            ds.add_coord("time", dims=["time"], data=np.arange(5))  # Should be 10

    def test_validate_strict_coords(self):
        """Test strict coordinate validation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_dim("lat", 5)

        # Add variable without corresponding coordinate
        ds.add_variable("temperature", dims=["time", "lat"])

        # Should pass without strict_coords
        ds.validate(strict_coords=False)

        # Should fail with strict_coords
        with pytest.raises(ValueError, match="Missing coordinate"):
            ds.validate(strict_coords=True)


class TestDimensionInference:
    """Test automatic dimension inference."""

    def test_infer_and_register_dims(self):
        """Test inferring dimensions from data."""
        ds = DummyDataset()

        arr = DummyArray(dims=["time", "lat"], data=np.random.rand(10, 5))
        ds._infer_and_register_dims(arr)

        assert ds.dims == {"time": 10, "lat": 5}

    def test_infer_dims_conflict(self):
        """Test dimension size conflict detection."""
        ds = DummyDataset()
        ds.add_dim("time", 10)

        # Try to add array with conflicting dimension size
        arr = DummyArray(dims=["time"], data=np.arange(5))  # Size 5, not 10

        with pytest.raises(ValueError, match="Dimension mismatch"):
            ds._infer_and_register_dims(arr)

    def test_infer_dims_multiple_arrays(self):
        """Test inferring dimensions from multiple arrays."""
        ds = DummyDataset()

        arr1 = DummyArray(dims=["time"], data=np.arange(10))
        arr2 = DummyArray(dims=["lat"], data=np.linspace(-90, 90, 5))
        arr3 = DummyArray(dims=["time", "lat"], data=np.random.rand(10, 5))

        ds._infer_and_register_dims(arr1)
        ds._infer_and_register_dims(arr2)
        ds._infer_and_register_dims(arr3)

        assert ds.dims == {"time": 10, "lat": 5}
