"""Tests for data generation functionality (DataGenerationMixin)."""

import numpy as np

from dummyxarray import DummyDataset


class TestPopulateWithRandomData:
    """Test random data population functionality."""

    def test_populate_basic(self, dataset_with_coords):
        """Test basic data population."""
        # Initially no data
        assert dataset_with_coords.coords["time"].data is None

        # Populate
        dataset_with_coords.populate_with_random_data(seed=42)

        # Now has data
        assert dataset_with_coords.coords["time"].data is not None
        assert dataset_with_coords.coords["lat"].data is not None
        assert dataset_with_coords.coords["lon"].data is not None

    def test_populate_reproducible(self, dataset_with_coords):
        """Test that population is reproducible with seed."""
        ds1 = dataset_with_coords
        ds1.populate_with_random_data(seed=42)
        data1 = ds1.coords["time"].data.copy()

        # Create another dataset
        ds2 = DummyDataset()
        ds2.add_dim("time", 10)
        ds2.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds2.populate_with_random_data(seed=42)
        data2 = ds2.coords["time"].data

        np.testing.assert_array_equal(data1, data2)

    def test_populate_method_chaining(self, dataset_with_coords):
        """Test that populate returns self for chaining."""
        result = dataset_with_coords.populate_with_random_data(seed=42)
        assert result is dataset_with_coords


class TestCoordinateDataGeneration:
    """Test coordinate-specific data generation."""

    def test_generate_time_coordinate(self):
        """Test time coordinate data generation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        ds.populate_with_random_data(seed=42)

        # Time should be sequential integers
        assert isinstance(ds.coords["time"].data, np.ndarray)
        assert len(ds.coords["time"].data) == 10
        np.testing.assert_array_equal(ds.coords["time"].data, np.arange(10))

    def test_generate_latitude_coordinate(self):
        """Test latitude coordinate data generation."""
        ds = DummyDataset()
        ds.add_dim("lat", 5)
        ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        ds.populate_with_random_data(seed=42)

        # Latitude should be in range [-90, 90]
        lat_data = ds.coords["lat"].data
        assert lat_data.min() >= -90
        assert lat_data.max() <= 90
        assert len(lat_data) == 5

    def test_generate_longitude_coordinate(self):
        """Test longitude coordinate data generation."""
        ds = DummyDataset()
        ds.add_dim("lon", 8)
        ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
        ds.populate_with_random_data(seed=42)

        # Longitude should be in range [-180, 180]
        lon_data = ds.coords["lon"].data
        assert lon_data.min() >= -180
        assert lon_data.max() <= 180
        assert len(lon_data) == 8

    def test_generate_pressure_coordinate(self):
        """Test pressure level coordinate data generation."""
        ds = DummyDataset()
        ds.add_dim("plev", 5)
        ds.add_coord("plev", dims=["plev"], attrs={"units": "hPa"})
        ds.populate_with_random_data(seed=42)

        # Pressure should be decreasing (high to low)
        plev_data = ds.coords["plev"].data
        assert len(plev_data) == 5
        assert plev_data[0] > plev_data[-1]  # High pressure to low pressure


class TestVariableDataGeneration:
    """Test variable-specific data generation."""

    def test_generate_temperature_kelvin(self):
        """Test temperature variable in Kelvin."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable(
            "temperature", dims=["time"], attrs={"units": "K", "standard_name": "air_temperature"}
        )
        ds.populate_with_random_data(seed=42)

        # Temperature in Kelvin should be in realistic range
        temp_data = ds.variables["temperature"].data
        assert temp_data.min() >= 250
        assert temp_data.max() <= 310

    def test_generate_temperature_celsius(self):
        """Test temperature variable in Celsius."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable(
            "temperature", dims=["time"], attrs={"units": "C", "standard_name": "air_temperature"}
        )
        ds.populate_with_random_data(seed=42)

        # Temperature in Celsius should be in realistic range
        temp_data = ds.variables["temperature"].data
        assert temp_data.min() >= -30
        assert temp_data.max() <= 40

    def test_generate_precipitation(self):
        """Test precipitation variable generation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("pr", dims=["time"], attrs={"standard_name": "precipitation"})
        ds.populate_with_random_data(seed=42)

        # Precipitation should be non-negative
        pr_data = ds.variables["pr"].data
        assert (pr_data >= 0).all()

    def test_generate_wind_components(self):
        """Test wind component variable generation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("u_wind", dims=["time"], attrs={"standard_name": "eastward_wind"})
        ds.add_variable("v_wind", dims=["time"], attrs={"standard_name": "northward_wind"})
        ds.populate_with_random_data(seed=42)

        # Wind components can be negative
        u_data = ds.variables["u_wind"].data
        v_data = ds.variables["v_wind"].data

        assert u_data.min() >= -20
        assert u_data.max() <= 20
        assert v_data.min() >= -20
        assert v_data.max() <= 20

    def test_generate_humidity(self):
        """Test humidity variable generation."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("rh", dims=["time"], attrs={"standard_name": "relative_humidity"})
        ds.populate_with_random_data(seed=42)

        # Relative humidity should be 0-100%
        rh_data = ds.variables["rh"].data
        assert rh_data.min() >= 20
        assert rh_data.max() <= 100

    def test_generate_default_variable(self):
        """Test default variable generation (no specific hints)."""
        ds = DummyDataset()
        ds.add_dim("time", 10)
        ds.add_variable("unknown_var", dims=["time"])
        ds.populate_with_random_data(seed=42)

        # Should generate standard normal distribution
        data = ds.variables["unknown_var"].data
        assert isinstance(data, np.ndarray)
        assert len(data) == 10
