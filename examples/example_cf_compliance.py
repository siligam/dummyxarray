"""
Demonstration of CF compliance workflow in dummyxarray.

This example shows how to:
1. Capture initial dataset state
2. Reset history to track only CF compliance changes
3. Infer and set axis attributes
4. Validate CF compliance
5. Review transformations via provenance tracking
"""

from dummyxarray import DummyDataset

print("=" * 70)
print("CF Compliance Workflow Demo")
print("=" * 70)

# ============================================================================
# Step 1: Build initial dataset (simulating from_xarray capture)
# ============================================================================
print("\n📦 Step 1: Building initial dataset...")
ds = DummyDataset()

# Add dimensions
ds.add_dim("time", 120)
ds.add_dim("lat", 64)
ds.add_dim("lon", 128)
ds.add_dim("lev", 19)

# Add coordinates (minimal metadata)
ds.add_coord("time", dims=["time"])
ds.add_coord("lat", dims=["lat"])
ds.add_coord("lon", dims=["lon"])
ds.add_coord("lev", dims=["lev"])

# Add variables
ds.add_variable("temperature", dims=["time", "lev", "lat", "lon"])
ds.add_variable("pressure", dims=["time", "lev", "lat", "lon"])

print(f"  ✓ Created dataset with {len(ds.dims)} dimensions")
print(f"  ✓ Added {len(ds.coords)} coordinates")
print(f"  ✓ Added {len(ds.variables)} variables")
print(f"  ✓ History has {len(ds.get_history())} operations")

# ============================================================================
# Step 2: Reset history to track only CF compliance changes
# ============================================================================
print("\n🔄 Step 2: Resetting history...")
ds.reset_history()
print(f"  ✓ History reset - now has {len(ds.get_history())} operations")
print("  ℹ️  Future changes will be tracked from this point")

# ============================================================================
# Step 3: Add CF-required metadata
# ============================================================================
print("\n📝 Step 3: Adding CF-required metadata...")

# Add units to coordinates
ds.coords["time"].attrs["units"] = "days since 2000-01-01"
ds.coords["lat"].attrs["units"] = "degrees_north"
ds.coords["lon"].attrs["units"] = "degrees_east"
ds.coords["lev"].attrs["units"] = "hPa"

# Add standard_name to coordinates
ds.coords["time"].attrs["standard_name"] = "time"
ds.coords["lat"].attrs["standard_name"] = "latitude"
ds.coords["lon"].attrs["standard_name"] = "longitude"
ds.coords["lev"].attrs["standard_name"] = "air_pressure"

# Add metadata to variables
ds.variables["temperature"].attrs.update(
    {"units": "K", "standard_name": "air_temperature", "long_name": "Air Temperature"}
)

ds.variables["pressure"].attrs.update(
    {"units": "Pa", "standard_name": "air_pressure", "long_name": "Air Pressure"}
)

print("  ✓ Added units to all coordinates")
print("  ✓ Added standard_name to coordinates and variables")

# ============================================================================
# Step 4: Infer and set axis attributes
# ============================================================================
print("\n🔍 Step 4: Inferring axis attributes...")

# First, let's see what can be inferred
inferred_axes = ds.infer_axis()
print("  Inferred axes:")
for coord, axis in inferred_axes.items():
    print(f"    • {coord}: {axis}")

# Set axis attributes
assigned = ds.set_axis_attributes()
print(f"\n  ✓ Set axis attributes for {len(assigned)} coordinates")

# Verify axes
print("\n  Axis assignments:")
for axis_type in ["T", "Z", "Y", "X"]:
    coords = ds.get_axis_coordinates(axis_type)
    if coords:
        print(f"    • {axis_type}-axis: {', '.join(coords)}")

# ============================================================================
# Step 5: Add global CF attributes
# ============================================================================
print("\n🌍 Step 5: Adding global CF attributes...")
ds.assign_attrs(
    Conventions="CF-1.8",
    title="Example Climate Dataset",
    institution="DKRZ",
    source="Model output",
    history="Created for CF compliance demonstration",
)
print("  ✓ Added Conventions and other global attributes")

# ============================================================================
# Step 6: Validate CF compliance
# ============================================================================
print("\n✅ Step 6: Validating CF compliance...")
result = ds.validate_cf()

print("\n  Validation Results:")
print(f"    • Errors: {len(result['errors'])}")
print(f"    • Warnings: {len(result['warnings'])}")

if result["warnings"]:
    print("\n  Remaining warnings:")
    for warning in result["warnings"][:5]:  # Show first 5
        print(f"    ⚠️  {warning}")
    if len(result["warnings"]) > 5:
        print(f"    ... and {len(result['warnings']) - 5} more")

# ============================================================================
# Step 7: Review transformations via provenance
# ============================================================================
print("\n" + "=" * 70)
print("PROVENANCE: What Changed to Make Dataset CF-Compliant")
print("=" * 70)

# Show compact provenance
print(ds.visualize_provenance(compact=True))

# ============================================================================
# Step 8: Query specific changes
# ============================================================================
print("\n" + "=" * 70)
print("QUERYING SPECIFIC CHANGES")
print("=" * 70)

# Get all provenance
prov_list = ds.get_provenance()
print(f"\nTotal operations with tracked changes: {len(prov_list)}")

# Find when axis attributes were added
print("\n🔍 Finding when axis attributes were added:")
for prov_entry in prov_list:
    if "modified" in prov_entry.get("provenance", {}):
        for _key, change in prov_entry["provenance"]["modified"].items():
            if isinstance(change, dict) and "axis" in str(change):
                print(f"  Operation {prov_entry['index']}: Added axis attribute")
                break

# ============================================================================
# Use Case: Dimension Ordering Check
# ============================================================================
print("\n" + "=" * 70)
print("USE CASE: Checking Dimension Ordering")
print("=" * 70)

print("\nCF recommends dimension order: T, Z, Y, X")
print("\nCurrent variable dimensions:")
for var_name, var in ds.variables.items():
    if var.dims:
        # Get axis types for each dimension
        dim_info = []
        for dim in var.dims:
            if dim in ds.coords:
                axis = ds.coords[dim].attrs.get("axis", "?")
                dim_info.append(f"{dim}({axis})")
            else:
                dim_info.append(f"{dim}(?)")
        print(f"  • {var_name}: {' × '.join(dim_info)}")

# ============================================================================
# Use Case: Export CF-compliant specification
# ============================================================================
print("\n" + "=" * 70)
print("USE CASE: Export CF-Compliant Specification")
print("=" * 70)

# Export to YAML
yaml_spec = ds.to_yaml()
print("\n📄 Dataset can be exported to YAML:")
print(yaml_spec[:500] + "...")
print(f"\nTotal YAML size: {len(yaml_spec)} characters")

# ============================================================================
# Workflow Summary
# ============================================================================
print("\n" + "=" * 70)
print("WORKFLOW SUMMARY")
print("=" * 70)
print(
    """
✅ Complete CF Compliance Workflow:

1. ✓ Captured initial dataset structure
2. ✓ Reset history to track only CF changes
3. ✓ Added required metadata (units, standard_name)
4. ✓ Inferred and set axis attributes (X/Y/Z/T)
5. ✓ Added global CF attributes (Conventions)
6. ✓ Validated CF compliance
7. ✓ Reviewed all transformations via provenance

Key Features Demonstrated:
  • reset_history() - Clear history after initial capture
  • infer_axis() - Auto-detect coordinate axes
  • set_axis_attributes() - Apply axis attributes
  • get_axis_coordinates() - Query by axis type
  • validate_cf() - Check CF compliance
  • visualize_provenance() - See what changed

Benefits:
  • Know exactly what was modified for CF compliance
  • Reproducible transformation workflow
  • Easy to apply same changes to similar datasets
  • Audit trail for compliance requirements
"""
)

print("=" * 70)
print("Demo complete!")
print("=" * 70)
