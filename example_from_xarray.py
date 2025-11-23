"""
Example: Creating DummyDataset from existing xarray.Dataset

This demonstrates how to extract metadata from an existing xarray.Dataset
to create a DummyDataset specification.
"""

import numpy as np
import xarray as xr
from dummyxarray import DummyDataset


def example_from_xarray_without_data():
    """Extract metadata from xarray without copying data."""
    print("=" * 60)
    print("EXAMPLE 1: From xarray.Dataset (metadata only)")
    print("=" * 60)
    
    # Create a sample xarray dataset
    xr_ds = xr.Dataset(
        data_vars={
            "temperature": (
                ["time", "lat", "lon"],
                np.random.rand(12, 64, 128) * 20 + 273.15,
                {
                    "long_name": "Near-Surface Air Temperature",
                    "units": "K",
                    "standard_name": "air_temperature"
                }
            ),
            "precipitation": (
                ["time", "lat", "lon"],
                np.random.rand(12, 64, 128) * 0.001,
                {
                    "long_name": "Precipitation Flux",
                    "units": "kg m-2 s-1",
                    "standard_name": "precipitation_flux"
                }
            )
        },
        coords={
            "time": (
                ["time"],
                np.arange(12),
                {"units": "months since 2020-01-01", "calendar": "standard"}
            ),
            "lat": (
                ["lat"],
                np.linspace(-90, 90, 64),
                {"units": "degrees_north", "standard_name": "latitude"}
            ),
            "lon": (
                ["lon"],
                np.linspace(-180, 180, 128),
                {"units": "degrees_east", "standard_name": "longitude"}
            )
        },
        attrs={
            "title": "Climate Model Output",
            "institution": "DKRZ",
            "Conventions": "CF-1.8",
            "source": "Example Model v1.0"
        }
    )
    
    print("\nOriginal xarray.Dataset:")
    print(xr_ds)
    
    # Extract metadata without data
    dummy_ds = DummyDataset.from_xarray(xr_ds, include_data=False)
    
    print("\n\nExtracted metadata as DummyDataset (YAML):")
    print(dummy_ds.to_yaml())
    
    # Save the specification
    dummy_ds.save_yaml("climate_model_spec.yaml")
    print("\nSaved specification to climate_model_spec.yaml")
    
    # Verify data was not copied
    print(f"\nData included: {dummy_ds.variables['temperature'].data is not None}")
    print(f"Dimensions captured: {dummy_ds.dims}")
    print(f"Variables captured: {list(dummy_ds.variables.keys())}")
    print(f"Coordinates captured: {list(dummy_ds.coords.keys())}")


def example_from_xarray_with_data():
    """Extract metadata and data from xarray."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: From xarray.Dataset (with data)")
    print("=" * 60)
    
    # Create a smaller dataset
    xr_ds = xr.Dataset(
        data_vars={
            "temperature": (["time"], np.array([273.15, 274.0, 275.5]))
        },
        coords={
            "time": (["time"], np.array([0, 1, 2]))
        },
        attrs={"title": "Small Example"}
    )
    
    # Extract with data
    dummy_ds = DummyDataset.from_xarray(xr_ds, include_data=True)
    
    print("\nDummyDataset with data:")
    print(f"Temperature data: {dummy_ds.variables['temperature'].data}")
    print(f"Time data: {dummy_ds.coords['time'].data}")
    
    # Can convert back to xarray
    xr_ds_reconstructed = dummy_ds.to_xarray()
    print("\nReconstructed xarray.Dataset:")
    print(xr_ds_reconstructed)


def example_workflow_template_from_existing():
    """Use case: Create template from existing dataset."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Workflow - Template from existing dataset")
    print("=" * 60)
    
    # Suppose you have an existing dataset
    existing_ds = xr.Dataset(
        data_vars={
            "tas": (["time", "lat", "lon"], np.random.rand(365, 90, 180)),
            "pr": (["time", "lat", "lon"], np.random.rand(365, 90, 180))
        },
        coords={
            "time": (["time"], np.arange(365)),
            "lat": (["lat"], np.linspace(-90, 90, 90)),
            "lon": (["lon"], np.linspace(-180, 180, 180))
        },
        attrs={"Conventions": "CF-1.8", "institution": "DKRZ"}
    )
    
    # Extract structure as template
    template = DummyDataset.from_xarray(existing_ds, include_data=False)
    
    # Save as reusable template
    template.save_yaml("daily_climate_template.yaml")
    print("Created template from existing dataset")
    
    # Later, load template for new dataset
    new_ds = DummyDataset.load_yaml("daily_climate_template.yaml")
    new_ds.set_global_attrs(experiment="new_run_001")
    
    # Add new data
    new_ds.variables["tas"].data = np.random.rand(365, 90, 180) * 20 + 273.15
    new_ds.variables["pr"].data = np.random.rand(365, 90, 180) * 0.001
    new_ds.coords["time"].data = np.arange(365)
    new_ds.coords["lat"].data = np.linspace(-90, 90, 90)
    new_ds.coords["lon"].data = np.linspace(-180, 180, 180)
    
    # Convert to xarray
    new_xr_ds = new_ds.to_xarray()
    print(f"\nNew dataset created from template:")
    print(f"  Experiment: {new_xr_ds.attrs['experiment']}")
    print(f"  Variables: {list(new_xr_ds.data_vars.keys())}")
    print(f"  Shape: {new_xr_ds['tas'].shape}")


def example_preserve_encoding():
    """Show that encoding is preserved."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Encoding preservation")
    print("=" * 60)
    
    # Create dataset with specific encoding
    xr_ds = xr.Dataset(
        data_vars={
            "temperature": (["time"], np.random.rand(100))
        }
    )
    
    # Set encoding
    xr_ds["temperature"].encoding = {
        "dtype": "float32",
        "chunks": (50,),
        "compressor": None
    }
    
    # Extract to DummyDataset
    dummy_ds = DummyDataset.from_xarray(xr_ds)
    
    print("\nOriginal encoding:")
    print(xr_ds["temperature"].encoding)
    
    print("\nPreserved in DummyDataset:")
    print(dummy_ds.variables["temperature"].encoding)
    
    # Verify it's applied when converting back
    xr_ds_new = dummy_ds.to_xarray()
    print("\nApplied to new xarray.Dataset:")
    print(xr_ds_new["temperature"].encoding)


if __name__ == "__main__":
    example_from_xarray_without_data()
    example_from_xarray_with_data()
    example_workflow_template_from_existing()
    example_preserve_encoding()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
