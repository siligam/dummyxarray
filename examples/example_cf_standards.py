"""Example: Using CF standards with cf_xarray.

This example demonstrates how to use cf_xarray for applying
community-agreed CF standards to your datasets.

cf_xarray is automatically installed as a dependency of dummyxarray.
"""

from dummyxarray import DummyDataset

# Create a dataset with minimal metadata
ds = DummyDataset()
ds.assign_attrs(
    Conventions="CF-1.8",
    title="CF Standards Example",
    institution="DKRZ",
)

# Add dimensions
ds.add_dim("time", 12)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)
ds.add_dim("lev", 5)

# Add coordinates with minimal CF metadata
# cf_xarray will detect and add the rest!
ds.add_coord(
    "time",
    dims=["time"],
    attrs={
        "units": "days since 2000-01-01 00:00:00",
        "calendar": "gregorian",
    },
)

ds.add_coord(
    "lat",
    dims=["lat"],
    attrs={
        "units": "degrees_north",
    },
)

ds.add_coord(
    "lon",
    dims=["lon"],
    attrs={
        "units": "degrees_east",
    },
)

ds.add_coord(
    "lev",
    dims=["lev"],
    attrs={
        "units": "hPa",
        "positive": "down",
    },
)

# Add variable
ds.add_variable(
    "temperature",
    dims=["time", "lev", "lat", "lon"],
    attrs={
        "standard_name": "air_temperature",
        "units": "K",
    },
)

print("=" * 60)
print("Dataset BEFORE applying CF standards")
print("=" * 60)
print(ds)
print("\nCoordinate attributes:")
for name, coord in ds.coords.items():
    print(f"\n{name}:")
    for attr, value in coord.attrs.items():
        print(f"  {attr}: {value}")

print("\nData status:")
print(f"  time: {ds.coords['time'].data}")
print(f"  lat: {ds.coords['lat'].data}")
print(f"  temperature: {ds.variables['temperature'].data}")

# Apply CF standards (works WITHOUT data!)
print("\n" + "=" * 60)
print("Applying CF Standards (using cf_xarray)")
print("=" * 60)

result = ds.apply_cf_standards(verbose=True)

print("\nAxes detected:")
for coord, axis in result["axes_detected"].items():
    print(f"  {coord}: {axis}")

print("\nAttributes added:")
for coord, attrs in result["attrs_added"].items():
    print(f"  {coord}:")
    for attr, value in attrs.items():
        print(f"    {attr}: {value}")

if result["warnings"]:
    print("\nWarnings:")
    for warning in result["warnings"]:
        print(f"  - {warning}")

# Show updated dataset
print("\n" + "=" * 60)
print("Dataset AFTER applying CF standards")
print("=" * 60)
print(ds)
print("\nCoordinate attributes:")
for name, coord in ds.coords.items():
    print(f"\n{name}:")
    for attr, value in coord.attrs.items():
        print(f"  {attr}: {value}")

# Validate CF metadata
print("\n" + "=" * 60)
print("Validating CF Metadata")
print("=" * 60)

validation = ds.validate_cf_metadata()

print(f"Valid: {validation['valid']}")
print(f"Errors: {len(validation['errors'])}")
print(f"Warnings: {len(validation['warnings'])}")
print(f"Suggestions: {len(validation['suggestions'])}")

if validation["errors"]:
    print("\nErrors:")
    for error in validation["errors"]:
        print(f"  - {error}")

if validation["warnings"]:
    print("\nWarnings:")
    for warning in validation["warnings"]:
        print(f"  - {warning}")

if validation["suggestions"]:
    print("\nSuggestions:")
    for suggestion in validation["suggestions"]:
        print(f"  - {suggestion}")

# Compare with built-in validation
print("\n" + "=" * 60)
print("Comparison: Built-in vs CF Standards")
print("=" * 60)

builtin_result = ds.validate_cf()
print("\nBuilt-in validation:")
print(f"  Errors: {len(builtin_result['errors'])}")
print(f"  Warnings: {len(builtin_result['warnings'])}")

print("\ncf_xarray validation:")
print(f"  Errors: {len(validation['errors'])}")
print(f"  Warnings: {len(validation['warnings'])}")
print(f"  Suggestions: {len(validation['suggestions'])}")

print("\nData status AFTER:")
print(f"  time: {ds.coords['time'].data}")
print(f"  lat: {ds.coords['lat'].data}")
print(f"  temperature: {ds.variables['temperature'].data}")
print("  → Data remains None! Metadata-only workflow preserved.")

print("\n" + "=" * 60)
print("✓ CF standards successfully applied!")
print("=" * 60)
print("\nKey benefits of using cf_xarray:")
print("  - Community-agreed standards")
print("  - Automatic axis detection")
print("  - Works WITHOUT data (metadata-only!)")
print("  - Consistent with xarray ecosystem")
print("  - Based on MetPy and Iris criteria")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("Built-in:    Fast, basic checks")
print("cf_xarray:   Community standards, comprehensive (now required)")
print("Recommended: Use apply_cf_standards() for production datasets")
