"""
Demonstration of provenance tracking in dummyxarray.

This example shows how to track changes to dataset state, capturing
what was modified, added, or removed in each operation - similar to
capturing provenance data in scientific workflows.
"""

import json

from dummyxarray import DummyDataset

print("=" * 70)
print("Provenance Tracking Demo")
print("=" * 70)

# Create a dataset and track changes
print("\n1. Building a dataset with tracked changes...")
ds = DummyDataset()

# Add dimensions
ds.add_dim("time", 10)
ds.add_dim("lat", 64)

# Add initial attributes
print("\n2. Setting initial attributes...")
ds.assign_attrs(units="degC", title="Temperature Data", version="1.0")

# Overwrite an attribute - this is where provenance shines!
print("\n3. Changing units from degC to K...")
ds.assign_attrs(units="K")

# Add a coordinate
print("\n4. Adding time coordinate...")
ds.add_coord("time", dims=["time"], attrs={"units": "days", "calendar": "gregorian"})

# Modify the coordinate
print("\n5. Updating time coordinate units...")
ds.add_coord("time", dims=["time"], attrs={"units": "hours", "calendar": "gregorian"})

# Add a variable
ds.add_variable("temperature", dims=["time", "lat"], attrs={"units": "K"})

# Update global attributes again
ds.assign_attrs(version="2.0", institution="DKRZ")

# Rename a variable (xarray-compatible API)
print("\n6. Renaming temperature variable to temp...")
ds.rename_vars(temperature="temp")

# Rename a dimension (xarray-compatible API)
print("\n7. Renaming lat dimension to latitude...")
ds.rename_dims(lat="latitude")

print("\n" + "=" * 70)
print("PROVENANCE VISUALIZATION")
print("=" * 70)
print(ds.visualize_provenance())

print("\n" + "=" * 70)
print("COMPACT PROVENANCE")
print("=" * 70)
print(ds.visualize_provenance(compact=True))

# Query specific changes
print("\n" + "=" * 70)
print("QUERYING SPECIFIC CHANGES")
print("=" * 70)

# Get all provenance
prov_list = ds.get_provenance()
print(f"\nTotal operations with changes: {len(prov_list)}")

# Find when units changed from degC to K
print("\n🔍 Finding when 'units' attribute changed from 'degC' to 'K':")
for prov_entry in prov_list:
    if prov_entry["func"] == "assign_attrs":
        prov = prov_entry["provenance"]
        if "modified" in prov and "units" in prov["modified"]:
            change = prov["modified"]["units"]
            if change["before"] == "degC" and change["after"] == "K":
                print(f"   Operation {prov_entry['index']}: {prov_entry['func']}")
                print(f"   Changed: units from '{change['before']}' to '{change['after']}'")

# Get provenance for a specific operation
print("\n🔍 Provenance for operation 3 (first assign_attrs):")
prov_op3 = ds.get_provenance(operation_index=3)
print(f"   {prov_op3}")

# Use case: Audit trail
print("\n" + "=" * 70)
print("USE CASE: AUDIT TRAIL")
print("=" * 70)
print("\nTracking all attribute modifications:")
for prov_entry in prov_list:
    if prov_entry["func"] == "assign_attrs" and "modified" in prov_entry["provenance"]:
        print(f"\nOperation {prov_entry['index']}:")
        for attr, change in prov_entry["provenance"]["modified"].items():
            before = change["before"] if change["before"] is not None else "None"
            after = change["after"]
            print(f"  • {attr}: {before} → {after}")

# Use case: Detect overwrites
print("\n" + "=" * 70)
print("USE CASE: DETECT OVERWRITES")
print("=" * 70)
print("\nFinding all overwrites (where before value was not None):")
overwrites = []
for prov_entry in prov_list:
    if "modified" in prov_entry.get("provenance", {}):
        for key, change in prov_entry["provenance"]["modified"].items():
            if isinstance(change, dict) and "before" in change:
                if change["before"] is not None:
                    overwrites.append(
                        {
                            "operation": prov_entry["index"],
                            "func": prov_entry["func"],
                            "key": key,
                            "before": change["before"],
                            "after": change["after"],
                        }
                    )

if overwrites:
    for ow in overwrites:
        print(f"\n⚠️  Operation {ow['operation']} ({ow['func']}):")
        print(f"   Overwrote '{ow['key']}': {ow['before']} → {ow['after']}")
else:
    print("No overwrites detected")

# Use case: History with provenance in JSON
print("\n" + "=" * 70)
print("USE CASE: EXPORT WITH PROVENANCE")
print("=" * 70)

# Get history with provenance
history_with_prov = ds.get_history(include_provenance=True)

# Show one example
print("\nExample operation with provenance (operation 3):")
print(json.dumps(history_with_prov[3], indent=2))

# Get history without provenance (smaller)
history_no_prov = ds.get_history(include_provenance=False)
prov_size = len(json.dumps(history_with_prov))
no_prov_size = len(json.dumps(history_no_prov))
print(f"\nHistory size with provenance: {prov_size} chars")
print(f"History size without provenance: {no_prov_size} chars")
print(f"Provenance adds: {prov_size - no_prov_size} chars")

# Use case: Reproducibility with change tracking
print("\n" + "=" * 70)
print("USE CASE: REPRODUCIBILITY WITH CHANGE TRACKING")
print("=" * 70)
print("\nProvenance ensures you know:")
print("  ✓ What was added (new dimensions, coords, variables)")
print("  ✓ What was modified (changed attributes, dimension sizes)")
print("  ✓ What was removed (if implemented)")
print("  ✓ The exact sequence of changes")
print("\nThis is crucial for:")
print("  • Scientific reproducibility")
print("  • Debugging unexpected behavior")
print("  • Understanding data lineage")
print("  • Compliance and auditing")
print("  • Collaborative workflows")

print("\n" + "=" * 70)
print("Demo complete!")
print("=" * 70)
print("\nKey features demonstrated:")
print("  ✓ Automatic provenance tracking")
print("  ✓ Before/after state capture")
print("  ✓ Overwrite detection")
print("  ✓ Audit trail generation")
print("  ✓ Provenance visualization")
print("  ✓ Selective provenance queries")
print("\nSimilar to:")
print("  • Git commit history (but for dataset operations)")
print("  • Database transaction logs")
print("  • Scientific workflow provenance (e.g., ProvONE, PROV-DM)")
