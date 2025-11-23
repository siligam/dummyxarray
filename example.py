"""
Example usage of DummyDataset

This script demonstrates the key features of the dummy xarray-like object:
1. Creating a dataset with dimensions, coordinates, and variables
2. Setting global attributes
3. Automatic dimension inference from data
4. Adding encoding information
5. Exporting to YAML/JSON
6. Validation
7. Converting to xarray.Dataset
8. Writing to Zarr format
"""

import numpy as np

from dummyxarray import DummyDataset


def example_basic_usage():
    """Basic example: create dataset with metadata only."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage (Metadata Only)")
    print("=" * 60)

    ds = DummyDataset()

    # Set global attributes
    ds.set_global_attrs(
        title="Test Climate Dataset",
        institution="DKRZ",
        experiment="historical",
        source="Example Model v1.0",
    )

    # Add dimensions
    ds.add_dim("time", 12)
    ds.add_dim("lat", 180)
    ds.add_dim("lon", 360)

    # Add coordinates (without data for now)
    ds.add_coord("time", ["time"], attrs={"units": "days since 2000-01-01"})
    ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
    ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

    # Add variables (without data)
    ds.add_variable(
        "tas",
        ["time", "lat", "lon"],
        attrs={"long_name": "Near-Surface Air Temperature", "units": "K"},
    )
    ds.add_variable(
        "pr", ["time", "lat", "lon"], attrs={"long_name": "Precipitation", "units": "kg m-2 s-1"}
    )

    # Export to YAML
    print("\nDataset structure (YAML):")
    print(ds.to_yaml())

    # Save to file
    ds.save_yaml("dataset_spec.yaml")
    print("Saved to dataset_spec.yaml")


def example_auto_inference():
    """Example with automatic dimension inference from data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Automatic Dimension Inference")
    print("=" * 60)

    ds = DummyDataset()

    ds.set_global_attrs(title="Auto-inferred Dataset", institution="DKRZ")

    # Create data with specific shape
    temp_data = np.random.rand(12, 64, 128)

    # Add variable with data - dimensions will be auto-inferred
    ds.add_variable("tas", data=temp_data, attrs={"units": "K", "long_name": "air_temperature"})

    print("\nDimensions were automatically inferred:")
    print(f"  {ds.dims}")

    print("\nDataset structure:")
    print(ds.to_yaml())


def example_with_encoding():
    """Example with encoding specifications for Zarr/NetCDF."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: With Encoding Specifications")
    print("=" * 60)

    ds = DummyDataset()

    ds.set_global_attrs(title="Dataset with Encoding")

    # Add dimensions
    ds.add_dim("time", 12)
    ds.add_dim("lat", 64)
    ds.add_dim("lon", 128)

    # Add coordinate with data and encoding
    time_data = np.arange(12)
    ds.add_coord(
        "time",
        ["time"],
        data=time_data,
        attrs={"units": "days since 2000-01-01"},
        encoding={"dtype": "int32"},
    )

    lat_data = np.linspace(-90, 90, 64)
    ds.add_coord(
        "lat",
        ["lat"],
        data=lat_data,
        attrs={"units": "degrees_north"},
        encoding={"dtype": "float32"},
    )

    lon_data = np.linspace(-180, 180, 128)
    ds.add_coord(
        "lon",
        ["lon"],
        data=lon_data,
        attrs={"units": "degrees_east"},
        encoding={"dtype": "float32"},
    )

    # Add variable with data and encoding
    temp_data = np.random.rand(12, 64, 128) * 20 + 273.15
    ds.add_variable(
        "tas",
        ["time", "lat", "lon"],
        data=temp_data,
        attrs={"long_name": "Near-Surface Air Temperature", "units": "K"},
        encoding={
            "dtype": "float32",
            "chunks": (6, 32, 64),
            "compressor": None,  # Can use zarr.Blosc() or similar
        },
    )

    print("\nDataset with encoding:")
    print(ds.to_yaml())

    # Validate the dataset
    print("\nValidating dataset...")
    try:
        ds.validate()
        print("✓ Validation passed!")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")

    return ds


def example_to_xarray(ds):
    """Convert dummy dataset to real xarray.Dataset."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Convert to xarray.Dataset")
    print("=" * 60)

    try:
        xr_ds = ds.to_xarray()
        print("\nSuccessfully converted to xarray.Dataset:")
        print(xr_ds)
    except Exception as e:
        print(f"Error converting to xarray: {e}")


def example_to_zarr(ds):
    """Write dataset to Zarr format."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Write to Zarr")
    print("=" * 60)

    try:
        ds.to_zarr("example_output.zarr", mode="w")
        print("✓ Successfully wrote to example_output.zarr")

        # Read it back with xarray
        import xarray as xr

        loaded = xr.open_zarr("example_output.zarr")
        print("\nLoaded back from Zarr:")
        print(loaded)
    except Exception as e:
        print(f"Error writing to Zarr: {e}")


def example_load_yaml():
    """Load dataset specification from YAML file."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Load from YAML")
    print("=" * 60)

    try:
        loaded_ds = DummyDataset.load_yaml("dataset_spec.yaml")
        print("\nLoaded dataset from YAML:")
        print(loaded_ds.to_yaml())
    except FileNotFoundError:
        print("dataset_spec.yaml not found. Run example_basic_usage() first.")
    except Exception as e:
        print(f"Error loading YAML: {e}")


def example_validation_errors():
    """Demonstrate validation catching errors."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Validation Error Detection")
    print("=" * 60)

    ds = DummyDataset()

    # Add a variable with unknown dimension
    ds.add_variable("bad_var", dims=["unknown_dim"], attrs={"units": "K"})

    print("\nAttempting to validate dataset with unknown dimension...")
    try:
        ds.validate()
        print("✓ Validation passed")
    except ValueError as e:
        print(f"✗ Validation failed (as expected):\n{e}")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_auto_inference()

    # Example with encoding returns dataset for further use
    ds_with_data = example_with_encoding()

    # Use the dataset with data for xarray and Zarr examples
    example_to_xarray(ds_with_data)
    example_to_zarr(ds_with_data)

    # Load from YAML
    example_load_yaml()

    # Demonstrate validation
    example_validation_errors()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
