"""
Example: Multi-file Dataset Support

This example demonstrates how to use DummyDataset.open_mfdataset() to work with
multiple NetCDF files and track which files contain specific coordinate ranges.
"""

import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

from dummyxarray import DummyDataset


def create_sample_files(output_dir):
    """Create sample NetCDF files for demonstration."""
    files = []

    # Create 3 files with different time ranges
    for i in range(3):
        filepath = output_dir / f"climate_data_{i:03d}.nc"

        # Each file covers 10 time steps
        time = np.arange(i * 10, (i + 1) * 10)
        lat = np.linspace(-90, 90, 64)
        lon = np.linspace(-180, 180, 128)

        # Create realistic climate data
        ds = xr.Dataset(
            {
                "temperature": (
                    ["time", "lat", "lon"],
                    np.random.randn(10, 64, 128) * 10 + 273.15,
                    {
                        "units": "K",
                        "standard_name": "air_temperature",
                        "long_name": "Near-Surface Air Temperature",
                    },
                ),
                "precipitation": (
                    ["time", "lat", "lon"],
                    np.random.rand(10, 64, 128) * 10,
                    {
                        "units": "mm/day",
                        "standard_name": "precipitation_flux",
                        "long_name": "Precipitation",
                    },
                ),
            },
            coords={
                "time": (
                    "time",
                    time,
                    {
                        "units": "days since 2000-01-01",
                        "calendar": "standard",
                        "axis": "T",
                    },
                ),
                "lat": (
                    "lat",
                    lat,
                    {
                        "units": "degrees_north",
                        "standard_name": "latitude",
                        "axis": "Y",
                    },
                ),
                "lon": (
                    "lon",
                    lon,
                    {
                        "units": "degrees_east",
                        "standard_name": "longitude",
                        "axis": "X",
                    },
                ),
            },
            attrs={
                "Conventions": "CF-1.8",
                "title": f"Climate Model Output - File {i}",
                "institution": "Example Climate Research Center",
                "source": "Example Climate Model v1.0",
                "history": "Created for demonstration purposes",
            },
        )

        ds.to_netcdf(filepath)
        files.append(filepath)
        print(f"Created: {filepath.name}")

    return files


def main():
    """Demonstrate multi-file dataset functionality."""
    print("=" * 70)
    print("Multi-file Dataset Example")
    print("=" * 70)

    # Create temporary directory and sample files
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        print("\n1. Creating sample NetCDF files...")
        create_sample_files(output_dir)

        print("\n2. Opening multiple files with DummyDataset.open_mfdataset()...")
        ds = DummyDataset.open_mfdataset(
            str(output_dir / "climate_data_*.nc"), concat_dim="time"
        )

        print("\n3. Dataset structure:")
        print(ds)

        print("\n4. File tracking information:")
        print(f"   File tracking enabled: {ds.is_file_tracking_enabled}")
        print(f"   Concatenation dimension: {ds.concat_dim}")
        print(f"   Number of tracked files: {len(ds.file_sources)}")

        print("\n5. Detailed file information:")
        for filepath, info in ds.file_sources.items():
            filename = Path(filepath).name
            coord_range = info["coord_range"]
            print(f"\n   {filename}:")
            print(f"     Time range: {coord_range[0]} to {coord_range[1]}")
            print(f"     Variables: {', '.join(info['metadata']['variables'])}")

        print("\n6. Querying source files:")

        # Query all files
        all_files = ds.get_source_files()
        print(f"\n   All files: {len(all_files)} files")
        for f in all_files:
            print(f"     - {Path(f).name}")

        # Query with no bounds (returns all)
        files_no_bounds = ds.get_source_files(time=slice(None, None))
        print(f"\n   Files with no time bounds: {len(files_no_bounds)} files")

        print("\n7. Manual file tracking example:")
        manual_ds = DummyDataset()
        manual_ds.enable_file_tracking(concat_dim="time")

        # Manually add file sources
        manual_ds.add_file_source(
            "model_run_001.nc",
            coord_range=(0, 365),
            metadata={"institution": "DKRZ", "model": "ICON"},
        )
        manual_ds.add_file_source(
            "model_run_002.nc",
            coord_range=(365, 730),
            metadata={"institution": "DKRZ", "model": "ICON"},
        )

        print("   Manually tracked files:")
        for filepath in manual_ds.file_sources:
            info = manual_ds.get_file_info(filepath)
            print(f"     {filepath}: time range {info['coord_range']}")

        print("\n8. Best practices:")
        print("   ✓ Use glob patterns for convenience: 'data/*.nc'")
        print("   ✓ Ensure files have compatible structures")
        print("   ✓ Query with compatible coordinate types")
        print("   ✓ Use file tracking to optimize data access patterns")
        print("   ✓ Metadata-only approach keeps memory usage low")

        print("\n" + "=" * 70)
        print("Example completed successfully!")
        print("=" * 70)


if __name__ == "__main__":
    main()
