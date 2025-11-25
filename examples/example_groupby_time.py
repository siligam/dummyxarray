"""
Example: Time-Based Grouping with DummyDataset
===============================================

This example demonstrates how to use the groupby_time() feature to split
multi-file datasets into time-based groups for analysis planning.

Features demonstrated:
- Automatic frequency inference
- Grouping by decades, years, and months
- Unit normalization
- File tracking in groups
- Calendar support
"""

import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

from dummyxarray import DummyDataset


def create_sample_climate_data(tmp_dir, n_years=30, freq="daily"):
    """Create sample NetCDF files for demonstration."""
    files = []

    if freq == "daily":
        # Create 30 years of daily data (3 files, 10 years each)
        for i in range(3):
            filepath = tmp_dir / f"tas_day_{i:03d}.nc"
            start_year = 2000 + i * 10

            # 10 years * 365 days (simplified, no leap years)
            n_days = 3650
            time = np.arange(0, n_days)

            ds = xr.Dataset(
                {
                    "tas": (["time", "lat", "lon"], np.random.rand(n_days, 10, 20) * 30 + 273.15),
                    "pr": (["time", "lat", "lon"], np.random.rand(n_days, 10, 20) * 10),
                },
                coords={
                    "time": time,
                    "lat": np.linspace(-90, 90, 10),
                    "lon": np.linspace(-180, 180, 20),
                },
            )

            ds["tas"].attrs = {
                "long_name": "Near-Surface Air Temperature",
                "units": "K",
                "standard_name": "air_temperature",
            }
            ds["pr"].attrs = {
                "long_name": "Precipitation",
                "units": "kg m-2 s-1",
                "standard_name": "precipitation_flux",
            }
            ds["time"].attrs = {
                "units": f"days since {start_year}-01-01 00:00:00",
                "calendar": "standard",
            }
            ds.attrs = {
                "Conventions": "CF-1.8",
                "title": f"Climate Model Output {start_year}-{start_year+9}",
                "institution": "Example Climate Research Center",
            }

            ds.to_netcdf(filepath)
            files.append(str(filepath))
            print(f"Created: {filepath.name}")

    elif freq == "hourly":
        # Create 2 years of hourly data (24 files, 1 month each)
        for i in range(24):
            filepath = tmp_dir / f"hourly_{i:03d}.nc"
            year = 2000 + i // 12
            month = (i % 12) + 1

            # Approximate days in month
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            n_hours = days_in_month[month - 1] * 24
            time = np.arange(0, n_hours)

            ds = xr.Dataset(
                {"temperature": (["time", "station"], np.random.rand(n_hours, 5) * 30)},
                coords={
                    "time": time,
                    "station": [f"STN{j:02d}" for j in range(5)],
                },
            )

            ds["time"].attrs = {
                "units": f"hours since {year}-{month:02d}-01 00:00:00",
                "calendar": "standard",
            }

            ds.to_netcdf(filepath)
            files.append(str(filepath))

    return files


def example_basic_grouping():
    """Example 1: Basic time-based grouping."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Decade Grouping")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Create sample data
        print("\n1. Creating 30 years of daily climate data...")
        files = create_sample_climate_data(tmp_dir, n_years=30, freq="daily")

        # Open all files
        print("\n2. Opening files with open_mfdataset()...")
        ds = DummyDataset.open_mfdataset(files, concat_dim="time")

        # Check frequency inference
        print("\n3. Frequency automatically inferred:")
        print(f"   Frequency: {ds.coords['time'].attrs['frequency']}")
        print(f"   Units: {ds.coords['time'].attrs['units']}")
        print(f"   Calendar: {ds.coords['time'].attrs.get('calendar', 'standard')}")
        print(f"   Total timesteps: {ds.dims['time']}")

        # Group by decades
        print("\n4. Grouping into decades...")
        decades = ds.groupby_time("10Y")

        print(f"   Number of decades: {len(decades)}")

        # Inspect each decade
        print("\n5. Decade details:")
        for i, decade in enumerate(decades):
            start_year = 2000 + i * 10
            print(f"\n   Decade {i} ({start_year}s):")
            print(f"     Time dimension: {decade.dims['time']} days")
            print(f"     Time units: {decade.coords['time'].attrs['units']}")
            print(f"     Variables: {list(decade.variables.keys())}")
            print(f"     Source files: {len(decade.get_source_files())}")


def example_different_frequencies():
    """Example 2: Grouping with different time frequencies."""
    print("\n" + "=" * 70)
    print("Example 2: Different Grouping Frequencies")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Create sample data
        print("\n1. Creating 30 years of daily data...")
        files = create_sample_climate_data(tmp_dir, n_years=30, freq="daily")
        ds = DummyDataset.open_mfdataset(files, concat_dim="time")

        # Try different grouping frequencies
        print("\n2. Grouping with different frequencies:")

        # Decades
        decades = ds.groupby_time("10Y")
        print(f"\n   10-year periods: {len(decades)} groups")
        print(f"     First group: {decades[0].dims['time']} timesteps")

        # 5-year periods
        quinquennials = ds.groupby_time("5Y")
        print(f"\n   5-year periods: {len(quinquennials)} groups")
        print(f"     First group: {quinquennials[0].dims['time']} timesteps")

        # Annual
        annual = ds.groupby_time("1Y")
        print(f"\n   Annual: {len(annual)} groups")
        print(f"     First group: {annual[0].dims['time']} timesteps")


def example_unit_normalization():
    """Example 3: Unit normalization in groups."""
    print("\n" + "=" * 70)
    print("Example 3: Unit Normalization")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Create sample data
        print("\n1. Creating sample data...")
        files = create_sample_climate_data(tmp_dir, n_years=30, freq="daily")
        ds = DummyDataset.open_mfdataset(files, concat_dim="time")

        # With normalization (default)
        print("\n2. With unit normalization (default):")
        decades_norm = ds.groupby_time("10Y", normalize_units=True)

        for i in range(min(3, len(decades_norm))):
            units = decades_norm[i].coords["time"].attrs["units"]
            print(f"   Decade {i}: {units}")

        # Without normalization
        print("\n3. Without unit normalization:")
        decades_no_norm = ds.groupby_time("10Y", normalize_units=False)

        for i in range(min(3, len(decades_no_norm))):
            units = decades_no_norm[i].coords["time"].attrs["units"]
            print(f"   Decade {i}: {units}")


def example_file_tracking():
    """Example 4: File tracking in grouped datasets."""
    print("\n" + "=" * 70)
    print("Example 4: File Tracking in Groups")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Create sample data
        print("\n1. Creating sample data...")
        files = create_sample_climate_data(tmp_dir, n_years=30, freq="daily")
        ds = DummyDataset.open_mfdataset(files, concat_dim="time")

        # Group by decades
        print("\n2. Grouping into decades...")
        decades = ds.groupby_time("10Y")

        # Check file tracking in each group
        print("\n3. Files in each decade:")
        for i, decade in enumerate(decades):
            tracked_files = decade.get_source_files()
            print(f"\n   Decade {i}:")
            print(f"     Number of files: {len(tracked_files)}")
            for f in tracked_files:
                filename = Path(f).name
                print(f"       - {filename}")


def example_use_case_planning():
    """Example 5: Real-world use case - analysis planning."""
    print("\n" + "=" * 70)
    print("Example 5: Analysis Planning Use Case")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Create sample data
        print("\n1. Scenario: Planning decadal climate analysis")
        print("   Dataset: 30 years of daily temperature and precipitation")

        files = create_sample_climate_data(tmp_dir, n_years=30, freq="daily")
        ds = DummyDataset.open_mfdataset(files, concat_dim="time")

        # Group by decades
        decades = ds.groupby_time("10Y")

        print(f"\n2. Analysis plan for {len(decades)} decades:")
        print("\n" + "-" * 70)

        for i, decade in enumerate(decades):
            start_year = 2000 + i * 10
            end_year = start_year + 9

            print(f"\nDecade {i+1}: {start_year}-{end_year}")
            print(f"  Time dimension: {decade.dims['time']} days")
            print(f"  Spatial dimensions: lat={decade.dims['lat']}, lon={decade.dims['lon']}")
            print(f"  Variables: {', '.join(decade.variables.keys())}")
            print(f"  Source files: {len(decade.get_source_files())}")

            # Estimate data size (if this were real data)
            n_timesteps = decade.dims["time"]
            n_lat = decade.dims["lat"]
            n_lon = decade.dims["lon"]
            n_vars = len(decade.variables)

            # Assuming float32 (4 bytes)
            size_mb = (n_timesteps * n_lat * n_lon * n_vars * 4) / (1024 * 1024)
            print(f"  Estimated size: {size_mb:.1f} MB")

            # Processing strategy
            if size_mb < 100:
                strategy = "Load entire decade into memory"
            elif size_mb < 1000:
                strategy = "Process in annual chunks"
            else:
                strategy = "Process in monthly chunks with dask"
            print(f"  Recommended strategy: {strategy}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Time-Based Grouping Examples")
    print("=" * 70)

    example_basic_grouping()
    example_different_frequencies()
    example_unit_normalization()
    example_file_tracking()
    example_use_case_planning()

    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)
    print("\nKey takeaways:")
    print("  ✓ Frequency is automatically inferred from time coordinates")
    print("  ✓ groupby_time() creates metadata-only groups")
    print("  ✓ Units can be normalized to each group's start time")
    print("  ✓ File tracking is preserved in grouped datasets")
    print("  ✓ Supports all cftime calendars")
    print("  ✓ Ideal for planning large-scale data processing")
    print()


if __name__ == "__main__":
    main()
