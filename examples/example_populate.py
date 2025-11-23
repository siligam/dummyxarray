"""
Example: Populating DummyDataset with Random but Meaningful Data

This demonstrates how to create a dataset structure and then populate it
with random data that is appropriate for each variable type.
"""

from dummyxarray import DummyDataset


def example_basic_populate():
    """Basic example of populating a dataset."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Population")
    print("=" * 60)

    # Create dataset structure
    ds = DummyDataset()
    ds.set_global_attrs(title="Climate Model Output", institution="DKRZ")

    # Define dimensions
    ds.add_dim("time", 12)
    ds.add_dim("lat", 64)
    ds.add_dim("lon", 128)

    # Add coordinates (without data)
    ds.add_coord("time", ["time"], attrs={"units": "months since 2020-01-01"})
    ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
    ds.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

    # Add variables (without data)
    ds.add_variable(
        "temperature",
        ["time", "lat", "lon"],
        attrs={"units": "K", "standard_name": "air_temperature"},
    )

    print("\nBefore population:")
    print(f"  Temperature has data: {ds.variables['temperature'].data is not None}")

    # Populate with random data
    ds.populate_with_random_data(seed=42)

    print("\nAfter population:")
    print(f"  Temperature has data: {ds.variables['temperature'].data is not None}")
    print(f"  Temperature shape: {ds.variables['temperature'].data.shape}")
    print(
        f"  Temperature range: [{ds.variables['temperature'].data.min():.2f}, "
        f"{ds.variables['temperature'].data.max():.2f}] K"
    )
    print(
        f"  Latitude range: [{ds.coords['lat'].data.min():.2f}, "
        f"{ds.coords['lat'].data.max():.2f}]"
    )


def example_different_variable_types():
    """Show how different variable types get appropriate data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Different Variable Types")
    print("=" * 60)

    ds = DummyDataset()
    ds.add_dim("time", 100)

    # Temperature
    ds.add_variable("tas", ["time"], attrs={"standard_name": "air_temperature", "units": "K"})

    # Precipitation
    ds.add_variable(
        "pr", ["time"], attrs={"standard_name": "precipitation_flux", "units": "kg m-2 s-1"}
    )

    # Sea level pressure
    ds.add_variable(
        "psl", ["time"], attrs={"standard_name": "air_pressure_at_sea_level", "units": "Pa"}
    )

    # Wind components
    ds.add_variable("ua", ["time"], attrs={"standard_name": "eastward_wind", "units": "m s-1"})
    ds.add_variable("va", ["time"], attrs={"standard_name": "northward_wind", "units": "m s-1"})

    # Relative humidity
    ds.add_variable("hur", ["time"], attrs={"standard_name": "relative_humidity", "units": "%"})

    # Populate
    ds.populate_with_random_data(seed=42)

    # Show statistics
    print("\nVariable Statistics:")
    print(
        f"  Temperature (tas):  {ds.variables['tas'].data.mean():.2f} K "
        f"[{ds.variables['tas'].data.min():.2f}, {ds.variables['tas'].data.max():.2f}]"
    )
    print(
        f"  Precipitation (pr): {ds.variables['pr'].data.mean():.6f} kg m-2 s-1 "
        f"(all positive: {(ds.variables['pr'].data >= 0).all()})"
    )
    print(
        f"  Pressure (psl):     {ds.variables['psl'].data.mean():.0f} Pa "
        f"[{ds.variables['psl'].data.min():.0f}, {ds.variables['psl'].data.max():.0f}]"
    )
    print(
        f"  U-wind (ua):        {ds.variables['ua'].data.mean():.2f} m/s "
        f"[{ds.variables['ua'].data.min():.2f}, {ds.variables['ua'].data.max():.2f}]"
    )
    print(
        f"  V-wind (va):        {ds.variables['va'].data.mean():.2f} m/s "
        f"[{ds.variables['va'].data.min():.2f}, {ds.variables['va'].data.max():.2f}]"
    )
    print(
        f"  Humidity (hur):     {ds.variables['hur'].data.mean():.1f}% "
        f"[{ds.variables['hur'].data.min():.1f}, {ds.variables['hur'].data.max():.1f}]"
    )


def example_from_yaml_then_populate():
    """Load structure from YAML, then populate with data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Load from YAML then Populate")
    print("=" * 60)

    # First, create and save a template
    template = DummyDataset()
    template.set_global_attrs(Conventions="CF-1.8", institution="DKRZ")
    template.add_dim("time", 365)
    template.add_dim("lat", 90)
    template.add_dim("lon", 180)

    template.add_coord("time", ["time"], attrs={"units": "days since 2020-01-01"})
    template.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})
    template.add_coord("lon", ["lon"], attrs={"units": "degrees_east"})

    template.add_variable(
        "tas", ["time", "lat", "lon"], attrs={"standard_name": "air_temperature", "units": "K"}
    )
    template.add_variable(
        "pr", ["time", "lat", "lon"], attrs={"standard_name": "precipitation_flux"}
    )

    template.save_yaml("climate_template.yaml")
    print("Saved template to climate_template.yaml")

    # Later, load and populate
    ds = DummyDataset.load_yaml("climate_template.yaml")
    print(f"\nLoaded template with {len(ds.variables)} variables")
    print(f"  Variables: {list(ds.variables.keys())}")
    print(f"  All have data: {all(v.data is not None for v in ds.variables.values())}")

    # Populate with random data
    ds.populate_with_random_data(seed=123)
    print("\nAfter population:")
    print(f"  All have data: {all(v.data is not None for v in ds.variables.values())}")
    print(f"  Total data points: {ds.variables['tas'].data.size:,}")


def example_convert_to_xarray():
    """Populate and convert to xarray."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Populate and Convert to xarray")
    print("=" * 60)

    ds = DummyDataset()
    ds.set_global_attrs(title="Test Dataset")
    ds.add_dim("time", 10)
    ds.add_dim("lat", 5)

    ds.add_coord("time", ["time"], attrs={"units": "days"})
    ds.add_coord("lat", ["lat"], attrs={"units": "degrees_north"})

    ds.add_variable(
        "temperature", ["time", "lat"], attrs={"units": "K", "standard_name": "air_temperature"}
    )

    # Populate and convert
    ds.populate_with_random_data(seed=42)
    xr_ds = ds.to_xarray()

    print("\nConverted to xarray.Dataset:")
    print(xr_ds)

    print("\nCan now use xarray operations:")
    print(f"  Mean temperature: {xr_ds['temperature'].mean().values:.2f} K")
    print(f"  Std temperature:  {xr_ds['temperature'].std().values:.2f} K")


def example_reproducible():
    """Show that results are reproducible with seed."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Reproducible Random Data")
    print("=" * 60)

    # Create two identical datasets
    ds1 = DummyDataset()
    ds1.add_dim("time", 5)
    ds1.add_variable("temp", ["time"], attrs={"units": "K"})
    ds1.populate_with_random_data(seed=999)

    ds2 = DummyDataset()
    ds2.add_dim("time", 5)
    ds2.add_variable("temp", ["time"], attrs={"units": "K"})
    ds2.populate_with_random_data(seed=999)

    print("\nDataset 1 temperature:", ds1.variables["temp"].data)
    print("Dataset 2 temperature:", ds2.variables["temp"].data)
    print(f"Identical: {(ds1.variables['temp'].data == ds2.variables['temp'].data).all()}")


if __name__ == "__main__":
    example_basic_populate()
    example_different_variable_types()
    example_from_yaml_then_populate()
    example_convert_to_xarray()
    example_reproducible()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
