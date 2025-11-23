"""
Demonstration of operation history tracking in dummyxarray.

This example shows how to record, export, and replay operations
to create reproducible dataset specifications.
"""

from dummyxarray import DummyDataset

print("=" * 70)
print("Operation History Tracking Demo")
print("=" * 70)

# Create a dataset with a series of operations
print("\n1. Building a dataset with operations...")
ds = DummyDataset()
ds.add_dim("time", 12)
ds.add_dim("lat", 180)
ds.add_dim("lon", 360)

ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

ds.add_variable("temperature", 
               dims=["time", "lat", "lon"],
               attrs={"units": "K", "long_name": "Near-Surface Air Temperature"},
               encoding={"dtype": "float32", "chunks": [6, 32, 64]})

ds.assign_attrs(
    title="Climate Model Output",
    institution="DKRZ",
    experiment="historical"
)

print(ds)

# Get the operation history
print("\n2. Retrieving operation history...")
history = ds.get_history()
print(f"Number of operations recorded: {len(history)}")
print("\nFirst few operations:")
for i, op in enumerate(history[:5]):
    print(f"  {i+1}. {op['func']}({', '.join(f'{k}={v}' for k, v in op['args'].items())})")

# Export history as JSON
print("\n3. Exporting history as JSON...")
json_history = ds.export_history('json')
print("JSON format (first 300 chars):")
print(json_history[:300] + "...")

# Export history as YAML
print("\n4. Exporting history as YAML...")
yaml_history = ds.export_history('yaml')
print("YAML format (first 300 chars):")
print(yaml_history[:300] + "...")

# Export history as Python code
print("\n5. Exporting history as executable Python code...")
python_code = ds.export_history('python')
print("Python code:")
print("-" * 70)
print(python_code)
print("-" * 70)

# Replay history to recreate the dataset
print("\n6. Replaying history to recreate the dataset...")
new_ds = DummyDataset.replay_history(history)

print("\nOriginal dataset dimensions:", ds.dims)
print("Recreated dataset dimensions:", new_ds.dims)
print("\nOriginal dataset attributes:", ds.attrs)
print("Recreated dataset attributes:", new_ds.attrs)
print("\nMatch:", ds.dims == new_ds.dims and ds.attrs == new_ds.attrs)

# Replay from JSON string
print("\n7. Replaying from JSON string...")
ds_from_json = DummyDataset.replay_history(json_history)
print("Recreated from JSON - dimensions:", ds_from_json.dims)

# Replay from YAML string
print("\n8. Replaying from YAML string...")
ds_from_yaml = DummyDataset.replay_history(yaml_history)
print("Recreated from YAML - dimensions:", ds_from_yaml.dims)

# Execute the Python code
print("\n9. Executing the exported Python code...")
namespace = {'DummyDataset': DummyDataset}
exec(python_code, namespace)
ds_from_code = namespace['ds']
print("Recreated from Python code - dimensions:", ds_from_code.dims)

# Use case: Save history for reproducibility
print("\n10. Use case: Saving history for reproducibility...")
with open("dataset_recipe.json", "w") as f:
    f.write(json_history)
print("Saved history to 'dataset_recipe.json'")

with open("dataset_recipe.py", "w") as f:
    f.write("from dummyxarray import DummyDataset\n\n")
    f.write(python_code)
print("Saved Python code to 'dataset_recipe.py'")

print("\n" + "=" * 70)
print("Demo complete!")
print("=" * 70)
print("\nKey features demonstrated:")
print("  ✓ Automatic operation recording")
print("  ✓ Export history as JSON, YAML, or Python code")
print("  ✓ Replay history to recreate datasets")
print("  ✓ Reproducible dataset specifications")
print("\nUse cases:")
print("  • Document dataset creation workflows")
print("  • Share dataset specifications as code")
print("  • Version control dataset structures")
print("  • Reproduce datasets from recipes")
print("  • Debug dataset construction issues")
