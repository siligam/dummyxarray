"""Example: Import dataset structure from ncdump header output.

This example demonstrates how to create a DummyDataset from the output
of `ncdump -h filename.nc`, which is useful for:

- Quickly replicating existing NetCDF structures
- Creating templates from real datasets
- Understanding dataset structure without loading data
"""

from dummyxarray import from_ncdump_header

# Example ncdump -h output
ncdump_header = """
netcdf climate_data {
dimensions:
    time = UNLIMITED ; // (365 currently)
    lev = 5 ;
    lat = 64 ;
    lon = 128 ;
variables:
    double time(time) ;
        time:units = "days since 2000-01-01 00:00:00" ;
        time:calendar = "gregorian" ;
        time:standard_name = "time" ;
        time:axis = "T" ;
    float lev(lev) ;
        lev:units = "hPa" ;
        lev:positive = "down" ;
        lev:standard_name = "air_pressure" ;
        lev:axis = "Z" ;
    double lat(lat) ;
        lat:units = "degrees_north" ;
        lat:standard_name = "latitude" ;
        lat:axis = "Y" ;
    double lon(lon) ;
        lon:units = "degrees_east" ;
        lon:standard_name = "longitude" ;
        lon:axis = "X" ;
    float temperature(time, lev, lat, lon) ;
        temperature:units = "K" ;
        temperature:standard_name = "air_temperature" ;
        temperature:long_name = "Air Temperature" ;
        temperature:cell_methods = "time: mean" ;
    float precipitation(time, lat, lon) ;
        precipitation:units = "kg m-2 s-1" ;
        precipitation:standard_name = "precipitation_flux" ;
        precipitation:long_name = "Precipitation" ;

// global attributes:
        :Conventions = "CF-1.8" ;
        :title = "Climate Model Output" ;
        :institution = "DKRZ" ;
        :source = "Climate Model v2.0" ;
        :history = "Created 2024-01-01" ;
}
"""

# Create DummyDataset from ncdump header
print("Creating DummyDataset from ncdump header...")
ds = from_ncdump_header(ncdump_header)

# Display the dataset
print("\n" + "=" * 60)
print("Dataset Structure")
print("=" * 60)
print(ds)

# Check dimensions
print("\n" + "=" * 60)
print("Dimensions")
print("=" * 60)
for dim_name, dim_size in ds.dims.items():
    print(f"  {dim_name}: {dim_size}")

# Check coordinates
print("\n" + "=" * 60)
print("Coordinates")
print("=" * 60)
for coord_name, coord in ds.coords.items():
    print(f"  {coord_name}:")
    print(f"    dims: {coord.dims}")
    print(f"    attrs: {coord.attrs}")

# Check variables
print("\n" + "=" * 60)
print("Variables")
print("=" * 60)
for var_name, var in ds.variables.items():
    print(f"  {var_name}:")
    print(f"    dims: {var.dims}")
    print(f"    attrs: {var.attrs}")

# Check global attributes
print("\n" + "=" * 60)
print("Global Attributes")
print("=" * 60)
for attr_name, attr_value in ds.attrs.items():
    print(f"  {attr_name}: {attr_value}")

# Populate with random data
print("\n" + "=" * 60)
print("Populating with random data...")
print("=" * 60)
ds.populate_with_random_data(seed=42)
print("✓ Data populated")

# Validate CF compliance
print("\n" + "=" * 60)
print("CF Compliance Check")
print("=" * 60)
result = ds.validate_cf()
print(f"Errors: {len(result['errors'])}")
print(f"Warnings: {len(result['warnings'])}")
if result["warnings"]:
    print("\nWarnings:")
    for warning in result["warnings"]:
        print(f"  - {warning}")

# Export to YAML template
print("\n" + "=" * 60)
print("Exporting to YAML template...")
print("=" * 60)
ds.save_yaml("ncdump_imported_template.yaml")
print("✓ Saved to ncdump_imported_template.yaml")

# Convert to xarray
print("\n" + "=" * 60)
print("Converting to xarray.Dataset...")
print("=" * 60)
xr_ds = ds.to_xarray()
print(xr_ds)

print("\n" + "=" * 60)
print("✓ Successfully imported and processed ncdump header!")
print("=" * 60)
