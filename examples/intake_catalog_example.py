#!/usr/bin/env python3
"""
Example script demonstrating dummyxarray Intake catalog functionality.
Shows both export and import capabilities for complete round-trip support.
"""

import os
import sys

# Add the src directory to the path so we can import dummyxarray
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import tempfile

import yaml

from dummyxarray import DummyDataset


def main():
    print("=== dummyxarray Intake Catalog Round-Trip Demo ===\n")

    print("1. Creating a sample DummyDataset...")

    # Create a dataset structure
    ds = DummyDataset()
    ds.assign_attrs(
        title="Climate Model Output",
        institution="Example Climate Center",
        Conventions="CF-1.8",
        project="CMIP6",
    )

    # Add dimensions
    ds.add_dim("time", 12)
    ds.add_dim("lat", 180)
    ds.add_dim("lon", 360)

    # Add coordinates
    ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
    ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
    ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

    # Add variables
    ds.add_variable(
        "temperature",
        dims=["time", "lat", "lon"],
        attrs={"standard_name": "air_temperature", "units": "K", "long_name": "Air Temperature"},
        encoding={"dtype": "float32", "chunks": [6, 32, 64]},
    )

    ds.add_variable(
        "precipitation",
        dims=["time", "lat", "lon"],
        attrs={
            "standard_name": "precipitation_flux",
            "units": "kg m-2 s-1",
            "long_name": "Precipitation Rate",
        },
        encoding={"dtype": "float32", "chunks": [6, 32, 64]},
    )

    print("✅ Original dataset created successfully!")
    print(f"   Dimensions: {ds.dims}")
    print(f"   Variables: {list(ds.variables.keys())}")
    print(f"   Coordinates: {list(ds.coords.keys())}")
    print(f"   Attributes: {list(ds.attrs.keys())}")

    print("\n2. Exporting to Intake catalog...")

    # Generate Intake catalog
    catalog_yaml = ds.to_intake_catalog(
        name="climate_data",
        description="Climate model output with temperature and precipitation",
        driver="zarr",
        data_path="data/climate_model_output.zarr",
    )

    print("✅ Catalog exported to YAML!")
    print("\n--- Generated Intake Catalog YAML ---")
    print(catalog_yaml)
    print("--- End Catalog ---\n")

    print("3. Saving catalog to file...")

    # Save catalog to file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        catalog_path = f.name

    ds.save_intake_catalog(
        catalog_path,
        name="climate_data",
        description="Climate model output with temperature and precipitation",
        driver="zarr",
        data_path="data/climate_model_output.zarr",
    )

    print(f"✅ Catalog saved to: {catalog_path}")

    print("\n4. Loading DummyDataset from catalog (round-trip test)...")

    # Load dataset back from catalog file
    loaded_ds = DummyDataset.from_intake_catalog(catalog_path, "climate_data")

    print("✅ Dataset loaded from catalog successfully!")
    print(f"   Dimensions: {loaded_ds.dims}")
    print(f"   Variables: {list(loaded_ds.variables.keys())}")
    print(f"   Coordinates: {list(loaded_ds.coords.keys())}")
    print(f"   Attributes: {list(loaded_ds.attrs.keys())}")

    print("\n5. Comparing original and loaded datasets...")

    # Compare structures
    dimensions_match = loaded_ds.dims == ds.dims
    variables_match = set(loaded_ds.variables.keys()) == set(ds.variables.keys())
    coords_match = set(loaded_ds.coords.keys()) == set(ds.coords.keys())

    # Check specific attributes
    original_attrs = {
        k: v
        for k, v in ds.attrs.items()
        if k.startswith(("title", "institution", "Conventions", "project"))
    }
    loaded_attrs = {
        k: v
        for k, v in loaded_ds.attrs.items()
        if k.startswith(("title", "institution", "Conventions", "project"))
    }
    attrs_match = original_attrs == loaded_attrs

    # Check variable details
    temp_orig = ds.variables["temperature"]
    temp_loaded = loaded_ds.variables["temperature"]
    temp_details_match = (
        temp_orig.dims == temp_loaded.dims
        and temp_orig.attrs == temp_loaded.attrs
        and temp_orig.encoding == temp_loaded.encoding
    )

    print(f"   Dimensions match: {'✅' if dimensions_match else '❌'}")
    print(f"   Variables match: {'✅' if variables_match else '❌'}")
    print(f"   Coordinates match: {'✅' if coords_match else '❌'}")
    print(f"   Dataset attributes match: {'✅' if attrs_match else '❌'}")
    print(f"   Variable details match: {'✅' if temp_details_match else '❌'}")

    print("\n6. Testing alternative loading methods...")

    # Load from dictionary
    catalog_dict = yaml.safe_load(catalog_yaml)
    loaded_ds_dict = DummyDataset.from_intake_catalog(catalog_dict, "climate_data")

    # Load using convenience method
    loaded_ds_conv = DummyDataset.load_intake_catalog(catalog_path, "climate_data")

    dict_match = loaded_ds.dims == loaded_ds_dict.dims
    conv_match = loaded_ds.dims == loaded_ds_conv.dims

    print(f"   Dictionary loading works: {'✅' if dict_match else '❌'}")
    print(f"   Convenience method works: {'✅' if conv_match else '❌'}")

    print("\n7. Testing catalog metadata preservation...")

    # Check that catalog-specific attributes were added
    catalog_attrs = {
        "intake_catalog_source": loaded_ds.attrs.get("intake_catalog_source"),
        "intake_driver": loaded_ds.attrs.get("intake_driver"),
        "intake_description": loaded_ds.attrs.get("intake_description"),
    }

    print(f"   Catalog source: {catalog_attrs['intake_catalog_source']}")
    print(f"   Driver: {catalog_attrs['intake_driver']}")
    print(f"   Description: {catalog_attrs['intake_description']}")

    # Clean up
    os.unlink(catalog_path)
    print(f"\n🧹 Cleaned up temporary file: {catalog_path}")

    # Final summary
    all_tests_pass = all(
        [
            dimensions_match,
            variables_match,
            coords_match,
            attrs_match,
            temp_details_match,
            dict_match,
            conv_match,
        ]
    )

    print(f"\n{'='*60}")
    if all_tests_pass:
        print("🎉 ALL TESTS PASSED! Intake catalog round-trip working perfectly!")
        print("\nFeatures demonstrated:")
        print("  ✅ Export DummyDataset to Intake catalog YAML")
        print("  ✅ Save catalog to file")
        print("  ✅ Load DummyDataset from catalog file")
        print("  ✅ Load from catalog dictionary")
        print("  ✅ Convenience method for file loading")
        print("  ✅ Complete metadata preservation")
        print("  ✅ Variable and encoding preservation")
        print("  ✅ Round-trip data integrity")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
