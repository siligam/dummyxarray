"""
Demonstration of history visualization in dummyxarray.

This example shows how to visualize operation history in different formats:
- Text (human-readable)
- DOT/Graphviz (for rendering graphs)
- Mermaid (for documentation and GitHub)
"""

from dummyxarray import DummyDataset

print("=" * 70)
print("History Visualization Demo")
print("=" * 70)

# Create a dataset with a series of operations
print("\n1. Building a climate dataset...")
ds = DummyDataset()
ds.add_dim("time", 365)
ds.add_dim("lat", 90)
ds.add_dim("lon", 180)

ds.add_coord("time", dims=["time"], attrs={"units": "days since 2020-01-01"})
ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})

ds.add_variable(
    "tas",
    dims=["time", "lat", "lon"],
    attrs={"units": "K", "long_name": "Near-Surface Air Temperature"},
    encoding={"dtype": "float32", "chunks": [30, 32, 64]},
)

ds.add_variable(
    "pr",
    dims=["time", "lat", "lon"],
    attrs={"units": "kg m-2 s-1", "long_name": "Precipitation"},
    encoding={"dtype": "float32", "chunks": [30, 32, 64]},
)

ds.assign_attrs(
    title="Climate Model Output",
    institution="DKRZ",
    experiment="historical",
    frequency="day",
)

print(ds)

# Text visualization - default (detailed)
print("\n" + "=" * 70)
print("2. Text Visualization (Detailed)")
print("=" * 70)
print(ds.visualize_history(format="text"))

# Text visualization - compact
print("\n" + "=" * 70)
print("3. Text Visualization (Compact)")
print("=" * 70)
print(ds.visualize_history(format="text", compact=True))

# Text visualization - without arguments
print("\n" + "=" * 70)
print("4. Text Visualization (No Arguments)")
print("=" * 70)
print(ds.visualize_history(format="text", show_args=False))

# DOT/Graphviz visualization
print("\n" + "=" * 70)
print("5. DOT/Graphviz Visualization")
print("=" * 70)
print("This format can be rendered with Graphviz tools:")
print()
dot_viz = ds.visualize_history(format="dot")
print(dot_viz)
print()
print("To render this graph:")
print("  1. Save to file: ds.visualize_history('dot') > graph.dot")
print("  2. Render: dot -Tpng graph.dot -o graph.png")
print("  3. Or use online tools: https://dreampuf.github.io/GraphvizOnline/")

# Save DOT file
with open("examples/dataset_history.dot", "w") as f:
    f.write(dot_viz)
print("\nSaved DOT file to 'examples/dataset_history.dot'")

# Mermaid visualization
print("\n" + "=" * 70)
print("6. Mermaid Diagram Visualization")
print("=" * 70)
print("This format works in GitHub, GitLab, and documentation:")
print()
mermaid_viz = ds.visualize_history(format="mermaid")
print(mermaid_viz)
print()
print("To use in Markdown:")
print("  ```mermaid")
print("  " + "\n  ".join(mermaid_viz.split("\n")))
print("  ```")

# Save Mermaid file
with open("examples/dataset_history.mmd", "w") as f:
    f.write(mermaid_viz)
print("\nSaved Mermaid file to 'examples/dataset_history.mmd'")

# Demonstrate with a simpler workflow
print("\n" + "=" * 70)
print("7. Simple Workflow Visualization")
print("=" * 70)
simple_ds = DummyDataset()
simple_ds.add_dim("time", 10)
simple_ds.add_coord("time", dims=["time"], attrs={"units": "days"})
simple_ds.add_variable("temperature", dims=["time"], attrs={"units": "K"})
simple_ds.assign_attrs(title="Simple Dataset")

print("\nText format:")
print(simple_ds.visualize_history(format="text", compact=True))

print("\nMermaid format:")
print(simple_ds.visualize_history(format="mermaid"))

# Use case: Debugging complex workflows
print("\n" + "=" * 70)
print("8. Use Case: Debugging Complex Workflows")
print("=" * 70)
print("When building complex datasets, visualization helps identify:")
print("  • Operation sequence and dependencies")
print("  • Number of operations per type")
print("  • Potential optimization opportunities")
print()
print("Example - our climate dataset:")
viz = ds.visualize_history(format="text")
print(viz[viz.find("Summary:") :])

# Use case: Documentation
print("\n" + "=" * 70)
print("9. Use Case: Documentation")
print("=" * 70)
print("Include visualizations in your documentation:")
print()
print("Example README.md section:")
print("```markdown")
print("## Dataset Construction")
print()
print("The dataset is built using the following operations:")
print()
print("```mermaid")
for line in simple_ds.visualize_history(format="mermaid").split("\n")[:6]:
    print(line)
print("...")
print("```")
print("```")

print("\n" + "=" * 70)
print("Demo complete!")
print("=" * 70)
print("\nKey features demonstrated:")
print("  ✓ Text visualization (detailed, compact, no-args)")
print("  ✓ DOT/Graphviz format for graph rendering")
print("  ✓ Mermaid format for documentation")
print("  ✓ Operation breakdown and statistics")
print("  ✓ Multiple use cases (debugging, documentation)")
print("\nVisualization formats:")
print("  • text    - Human-readable, terminal-friendly")
print("  • dot     - Graphviz format, renders to images")
print("  • mermaid - GitHub/GitLab compatible diagrams")
print("\nFiles created:")
print("  • examples/dataset_history.dot - Graphviz DOT file")
print("  • examples/dataset_history.mmd - Mermaid diagram file")
