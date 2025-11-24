"""Tests for multi-file dataset functionality."""

import numpy as np
import pytest
import xarray as xr

from dummyxarray import DummyDataset


@pytest.fixture
def temp_netcdf_files(tmp_path):
    """Create temporary NetCDF files for testing."""
    files = []

    # Create 3 files with time slices
    for i in range(3):
        filepath = tmp_path / f"test_file_{i}.nc"

        # Create a simple dataset
        time = np.arange(i * 10, (i + 1) * 10)
        lat = np.arange(0, 5)
        lon = np.arange(0, 10)

        ds = xr.Dataset(
            {
                "temperature": (
                    ["time", "lat", "lon"],
                    np.random.rand(10, 5, 10),
                    {"units": "K", "standard_name": "air_temperature"},
                ),
            },
            coords={
                "time": ("time", time, {"units": "days since 2000-01-01"}),
                "lat": ("lat", lat, {"units": "degrees_north"}),
                "lon": ("lon", lon, {"units": "degrees_east"}),
            },
            attrs={"Conventions": "CF-1.8", "title": f"Test file {i}"},
        )

        ds.to_netcdf(filepath)
        files.append(str(filepath))

    return files


def test_open_mfdataset_basic(temp_netcdf_files):
    """Test basic open_mfdataset functionality."""
    ds = DummyDataset.open_mfdataset(temp_netcdf_files, concat_dim="time")

    # Check that file tracking is enabled
    assert ds.is_file_tracking_enabled
    assert ds.concat_dim == "time"

    # Check that dimensions are correct (30 time steps total)
    assert ds.dims["time"] == 30
    assert ds.dims["lat"] == 5
    assert ds.dims["lon"] == 10

    # Check that variables exist
    assert "temperature" in ds.variables
    assert ds.variables["temperature"].attrs["units"] == "K"

    # Check that coordinates exist
    assert "time" in ds.coords
    assert "lat" in ds.coords
    assert "lon" in ds.coords


def test_file_tracking(temp_netcdf_files):
    """Test file tracking functionality."""
    ds = DummyDataset.open_mfdataset(temp_netcdf_files, concat_dim="time")

    # Check that all files are tracked
    assert len(ds.file_sources) == 3

    # Check file info
    for filepath in temp_netcdf_files:
        info = ds.get_file_info(filepath)
        assert "coord_range" in info
        assert "concat_dim" in info
        assert info["concat_dim"] == "time"


def test_get_source_files(temp_netcdf_files):
    """Test querying source files by coordinate range."""
    ds = DummyDataset.open_mfdataset(temp_netcdf_files, concat_dim="time")

    # Note: Files are opened with decode_times=False, so coordinates are numeric
    # This allows proper range queries

    # Query all files (no slice)
    files = ds.get_source_files()
    assert len(files) == 3

    # Query with None slice (should return all)
    files = ds.get_source_files(time=slice(None, None))
    assert len(files) == 3

    # Query specific range (should return only overlapping files)
    files = ds.get_source_files(time=slice(0, 10))
    assert len(files) >= 1  # At least the first file


def test_open_mfdataset_glob_pattern(tmp_path):
    """Test open_mfdataset with glob pattern."""
    # Create test files
    for i in range(2):
        filepath = tmp_path / f"data_{i}.nc"
        time = np.arange(i * 5, (i + 1) * 5)
        ds = xr.Dataset(
            {"temp": (["time"], np.random.rand(5))},
            coords={"time": ("time", time)},
        )
        ds.to_netcdf(filepath)

    # Open with glob pattern
    pattern = str(tmp_path / "data_*.nc")
    ds = DummyDataset.open_mfdataset(pattern, concat_dim="time")

    assert ds.is_file_tracking_enabled
    assert ds.dims["time"] == 10
    assert len(ds.file_sources) == 2


def test_open_mfdataset_validation(tmp_path):
    """Test that incompatible files raise errors."""
    # Create two files with different variables
    file1 = tmp_path / "file1.nc"
    ds1 = xr.Dataset(
        {"temp": (["time"], np.random.rand(5))},
        coords={"time": ("time", np.arange(5))},
    )
    ds1.to_netcdf(file1)

    file2 = tmp_path / "file2.nc"
    ds2 = xr.Dataset(
        {"pressure": (["time"], np.random.rand(5))},  # Different variable
        coords={"time": ("time", np.arange(5, 10))},
    )
    ds2.to_netcdf(file2)

    # Should raise error due to variable mismatch
    with pytest.raises(ValueError, match="Variable mismatch"):
        DummyDataset.open_mfdataset([str(file1), str(file2)], concat_dim="time")


def test_manual_file_tracking():
    """Test manual file tracking without opening files."""
    ds = DummyDataset()
    ds.enable_file_tracking(concat_dim="time")

    # Manually add file sources
    ds.add_file_source("file1.nc", coord_range=(0, 10))
    ds.add_file_source("file2.nc", coord_range=(10, 20))

    # Query files
    files = ds.get_source_files(time=slice(5, 15))
    assert len(files) == 2
    assert "file1.nc" in files
    assert "file2.nc" in files

    # Get file info
    info = ds.get_file_info("file1.nc")
    assert info["coord_range"] == (0, 10)
    assert info["concat_dim"] == "time"


def test_frequency_inference(tmp_path):
    """Test automatic frequency inference for time coordinates."""
    import numpy as np
    import xarray as xr

    # Create hourly data
    filepath = tmp_path / "hourly_data.nc"
    time = np.arange(0, 24)  # 24 hours
    ds_xr = xr.Dataset(
        {
            "temperature": (["time", "lat", "lon"], np.random.rand(24, 10, 10)),
        },
        coords={
            "time": time,
            "lat": np.linspace(-90, 90, 10),
            "lon": np.linspace(-180, 180, 10),
        },
    )
    ds_xr["time"].attrs["units"] = "hours since 2000-01-01 00:00:00"
    ds_xr["time"].attrs["calendar"] = "standard"
    ds_xr.to_netcdf(filepath)

    # Open with mfdataset
    ds = DummyDataset.open_mfdataset([str(filepath)], concat_dim="time")

    # Check frequency was inferred
    assert "frequency" in ds.coords["time"].attrs
    assert ds.coords["time"].attrs["frequency"] == "1H"


def test_groupby_time_decades(tmp_path):
    """Test grouping dataset by decades."""
    import numpy as np
    import xarray as xr

    # Create 30 years of daily data (3 files, 10 years each)
    files = []
    for i in range(3):
        filepath = tmp_path / f"data_{i}.nc"
        start_year = 2000 + i * 10
        # 10 years * 365 days (simplified, no leap years)
        time = np.arange(0, 3650)
        ds_xr = xr.Dataset(
            {
                "temperature": (["time", "lat"], np.random.rand(3650, 10)),
            },
            coords={
                "time": time,
                "lat": np.linspace(-90, 90, 10),
            },
        )
        ds_xr["time"].attrs["units"] = f"days since {start_year}-01-01 00:00:00"
        ds_xr["time"].attrs["calendar"] = "standard"
        ds_xr.to_netcdf(filepath)
        files.append(str(filepath))

    # Open all files
    ds = DummyDataset.open_mfdataset(files, concat_dim="time")

    # Check total size
    assert ds.dims["time"] == 10950  # 30 years * 365 days

    # Group by decades
    decades = ds.groupby_time("10Y", dim="time")

    # Should have 3 decades
    assert len(decades) == 3

    # Check first decade
    decade_0 = decades[0]
    # Approximate: 10 years * 365.25 days (accounting for leap years)
    assert 3650 <= decade_0.dims["time"] <= 3654
    assert "2000-01-01" in decade_0.coords["time"].attrs["units"]

    # Check second decade
    decade_1 = decades[1]
    assert 3650 <= decade_1.dims["time"] <= 3654
    assert "2010-01-01" in decade_1.coords["time"].attrs["units"]


def test_groupby_time_without_frequency():
    """Test that groupby_time raises error without frequency attribute."""
    ds = DummyDataset()
    ds.add_dim("time", 100)
    ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})

    # Should raise error because no frequency attribute
    with pytest.raises(ValueError, match="no frequency attribute"):
        ds.groupby_time("10Y")


def test_groupby_time_monthly(tmp_path):
    """Test grouping by months."""
    import numpy as np
    import xarray as xr

    # Create 1 year of daily data
    filepath = tmp_path / "daily_data.nc"
    time = np.arange(0, 365)
    ds_xr = xr.Dataset(
        {
            "temperature": (["time", "lat"], np.random.rand(365, 10)),
        },
        coords={
            "time": time,
            "lat": np.linspace(-90, 90, 10),
        },
    )
    ds_xr["time"].attrs["units"] = "days since 2000-01-01 00:00:00"
    ds_xr["time"].attrs["calendar"] = "standard"
    ds_xr.to_netcdf(filepath)

    # Open with mfdataset
    ds = DummyDataset.open_mfdataset([str(filepath)], concat_dim="time")

    # Group by months
    months = ds.groupby_time("1M", dim="time")

    # Should have 12 months
    assert len(months) == 12

    # Each month should have ~30 days (approximate)
    for month in months:
        assert 28 <= month.dims["time"] <= 31
