"""
Dummy Xarray-like Object

A lightweight xarray-like object that allows you to:
- Define dimensions and their sizes
- Add variables and coordinates with metadata
- Export to YAML/JSON
- Support for encoding (dtype, chunks, compression)
- Validate dataset structure
- Convert to real xarray.Dataset
- Write to Zarr format
"""

import json

import numpy as np
import yaml


class DummyArray:
    """Represents a single array (variable or coordinate) with metadata."""

    def __init__(self, dims=None, attrs=None, data=None, encoding=None, _record_history=True):
        """
        Initialize a DummyArray.

        Parameters
        ----------
        dims : list of str, optional
            List of dimension names
        attrs : dict, optional
            Metadata attributes
        data : array-like, optional
            Data array (numpy array or list)
        encoding : dict, optional
            Encoding parameters (dtype, chunks, compressor, fill_value, etc.)
        _record_history : bool, optional
            Whether to record operation history (default: True)
        """
        self.dims = dims
        self.attrs = attrs or {}
        self.data = data
        self.encoding = encoding or {}

        # Operation history tracking
        self._history = [] if _record_history else None
        if _record_history:
            # Record initialization
            init_args = {}
            if dims is not None:
                init_args["dims"] = dims
            if attrs:
                init_args["attrs"] = attrs
            if data is not None:
                init_args["data"] = "<data>"  # Don't store actual data
            if encoding:
                init_args["encoding"] = encoding
            self._record_operation("__init__", init_args)

    def __repr__(self):
        """Return a string representation of the DummyArray."""
        lines = ["<dummyxarray.DummyArray>"]

        # Dimensions
        if self.dims:
            dims_str = f"({', '.join(self.dims)})"
        else:
            dims_str = "()"
        lines.append(f"Dimensions: {dims_str}")

        # Data info
        if self.data is not None:
            data_array = np.asarray(self.data)
            lines.append(f"Shape: {data_array.shape}")
            lines.append(f"dtype: {data_array.dtype}")

            # Show a preview of the data
            if data_array.size <= 10:
                lines.append(f"Data: {data_array}")
            else:
                flat = data_array.flatten()
                preview = f"[{flat[0]}, {flat[1]}, ..., {flat[-1]}]"
                lines.append(f"Data: {preview}")
        else:
            lines.append("Data: None")

        # Attributes
        if self.attrs:
            lines.append("Attributes:")
            for key, value in self.attrs.items():
                value_str = str(value)
                if len(value_str) > 40:
                    value_str = value_str[:37] + "..."
                lines.append(f"    {key}: {value_str}")

        # Encoding
        if self.encoding:
            lines.append("Encoding:")
            for key, value in self.encoding.items():
                lines.append(f"    {key}: {value}")

        return "\n".join(lines)

    def infer_dims_from_data(self):
        """
        Infer dimension names and sizes from data shape.

        Returns
        -------
        dict
            Dictionary mapping dimension names to sizes
        """
        if self.data is not None:
            shape = np.asarray(self.data).shape
            if self.dims is None:
                self.dims = [f"dim_{i}" for i in range(len(shape))]
            return dict(zip(self.dims, shape))
        return {}

    def _record_operation(self, func_name, args):
        """
        Record an operation in the history.

        Parameters
        ----------
        func_name : str
            Name of the function/method called
        args : dict
            Arguments passed to the function
        """
        if self._history is not None:
            self._history.append({"func": func_name, "args": args})

    def get_history(self):
        """
        Get the operation history for this array.

        Returns
        -------
        list of dict
            List of operations, each with 'func' and 'args' keys

        Examples
        --------
        >>> arr = DummyArray(dims=["time"])
        >>> arr.assign_attrs(units="K")
        >>> arr.get_history()
        [{'func': '__init__', 'args': {'dims': ['time']}},
         {'func': 'assign_attrs', 'args': {'units': 'K'}}]
        """
        return self._history.copy() if self._history is not None else []

    def replay_history(self, history=None):
        """
        Replay a sequence of operations to recreate an array.

        Parameters
        ----------
        history : list of dict, optional
            History to replay. If None, uses this array's history.

        Returns
        -------
        DummyArray
            New array with operations replayed

        Examples
        --------
        >>> arr = DummyArray(dims=["time"])
        >>> arr.assign_attrs(units="K")
        >>> history = arr.get_history()
        >>> new_arr = DummyArray.replay_history(history)
        """
        if history is None:
            history = self.get_history()

        # Find __init__ operation
        init_op = next((op for op in history if op["func"] == "__init__"), None)
        if init_op:
            arr = DummyArray(**init_op["args"], _record_history=False)
        else:
            arr = DummyArray(_record_history=False)

        # Replay other operations
        for op in history:
            if op["func"] == "__init__":
                continue

            func = getattr(arr, op["func"], None)
            if func and callable(func):
                func(**op["args"])

        return arr

    def assign_attrs(self, **kwargs):
        """
        Assign new attributes to this array (xarray-compatible API).

        This method updates the array's attributes dictionary in-place.

        Parameters
        ----------
        **kwargs
            Attribute key-value pairs to assign

        Returns
        -------
        DummyArray
            Returns self for method chaining

        Examples
        --------
        >>> arr = DummyArray(dims=["time"])
        >>> arr.assign_attrs(units="K", long_name="Temperature")
        >>> arr.assign_attrs(standard_name="air_temperature")
        """
        self._record_operation("assign_attrs", kwargs)
        self.attrs.update(kwargs)
        return self

    def to_dict(self):
        """
        Export structure (without data) for serialization.

        Returns
        -------
        dict
            Dictionary representation of the array metadata
        """
        return {
            "dims": self.dims,
            "attrs": self.attrs,
            "encoding": self.encoding,
            "has_data": self.data is not None,
        }


class DummyDataset:
    """
    A dummy xarray-like dataset for building metadata specifications.

    This class allows you to define the structure of a dataset including
    dimensions, coordinates, variables, and global attributes before
    creating the actual xarray.Dataset with real data.
    """

    def __init__(self, _record_history=True):
        """
        Initialize an empty DummyDataset.

        Parameters
        ----------
        _record_history : bool, optional
            Whether to record operation history (default: True)
        """
        self.dims = {}  # dim_name → size
        self.coords = {}  # coord_name → DummyArray
        self.variables = {}  # var_name  → DummyArray
        self.attrs = {}  # global attributes

        # Operation history tracking
        self._history = [] if _record_history else None
        if _record_history:
            self._record_operation("__init__", {})

    def __repr__(self):
        """Return a string representation similar to xarray.Dataset."""
        lines = ["<dummyxarray.DummyDataset>"]

        # Dimensions
        if self.dims:
            lines.append("Dimensions:")
            dim_strs = [f"  {name}: {size}" for name, size in self.dims.items()]
            lines.extend(dim_strs)
        else:
            lines.append("Dimensions: ()")

        # Coordinates
        if self.coords:
            lines.append("Coordinates:")
            for name, arr in self.coords.items():
                dims_str = f"({', '.join(arr.dims)})" if arr.dims else "()"
                has_data = "✓" if arr.data is not None else "✗"
                dtype_str = f"{arr.data.dtype}" if arr.data is not None else "?"
                lines.append(f"  {has_data} {name:20s} {dims_str:20s} {dtype_str}")

        # Data variables
        if self.variables:
            lines.append("Data variables:")
            for name, arr in self.variables.items():
                dims_str = f"({', '.join(arr.dims)})" if arr.dims else "()"
                has_data = "✓" if arr.data is not None else "✗"
                dtype_str = f"{arr.data.dtype}" if arr.data is not None else "?"
                lines.append(f"  {has_data} {name:20s} {dims_str:20s} {dtype_str}")

        # Global attributes
        if self.attrs:
            lines.append("Attributes:")
            for key, value in self.attrs.items():
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                lines.append(f"    {key}: {value_str}")

        return "\n".join(lines)

    def __getattr__(self, name):
        """
        Allow attribute-style access to coordinates and variables.

        This enables xarray-style access like `ds.time` instead of `ds.coords['time']`.
        Coordinates take precedence over variables if both exist with the same name.

        Parameters
        ----------
        name : str
            Name of the coordinate or variable to access

        Returns
        -------
        DummyArray
            The coordinate or variable array

        Raises
        ------
        AttributeError
            If the name is not found in coords or variables
        """
        # Check coordinates first (like xarray does)
        if name in self.coords:
            return self.coords[name]
        # Then check variables
        if name in self.variables:
            return self.variables[name]
        # If not found, raise AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Handle attribute assignment.

        Special handling for internal attributes (dims, coords, variables, attrs).
        For other names, this could be extended to allow setting coords/variables.
        """
        # Internal attributes that should be set normally
        if name in ("dims", "coords", "variables", "attrs", "_history"):
            object.__setattr__(self, name, value)
        else:
            # For now, raise an error to avoid confusion
            # Could be extended to allow ds.time = DummyArray(...) in the future
            raise AttributeError(
                f"Cannot set attribute '{name}' directly. "
                f"Use ds.coords['{name}'] or ds.variables['{name}'] instead."
            )

    def __dir__(self):
        """
        Customize dir() output to include coordinates and variables.

        This makes tab-completion work in IPython/Jupyter.
        """
        # Get default attributes
        default_attrs = set(object.__dir__(self))
        # Add coordinate and variable names
        return sorted(default_attrs | set(self.coords.keys()) | set(self.variables.keys()))

    # ------------------------------------------------------------
    # Operation History Tracking
    # ------------------------------------------------------------

    def _record_operation(self, func_name, args, provenance=None):
        """
        Record an operation in the history with provenance information.

        Parameters
        ----------
        func_name : str
            Name of the function/method called
        args : dict
            Arguments passed to the function
        provenance : dict, optional
            Provenance information capturing state changes:
            - 'changes': dict of what changed (before -> after)
            - 'added': list of items added
            - 'removed': list of items removed
            - 'modified': dict of items modified with before/after values
        """
        if self._history is not None:
            entry = {"func": func_name, "args": args}
            if provenance:
                entry["provenance"] = provenance
            self._history.append(entry)

    def get_history(self, include_provenance=True):
        """
        Get the operation history for this dataset.

        Parameters
        ----------
        include_provenance : bool, optional
            Whether to include provenance information (default: True)

        Returns
        -------
        list of dict
            List of operations, each with 'func', 'args', and optionally 'provenance' keys

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.assign_attrs(title="Test")
        >>> ds.get_history()
        [{'func': '__init__', 'args': {}},
         {'func': 'add_dim', 'args': {'name': 'time', 'size': 10},
          'provenance': {'added': ['time']}},
         {'func': 'assign_attrs', 'args': {'title': 'Test'},
          'provenance': {'modified': {'title': {'before': None, 'after': 'Test'}}}}]
        """
        if self._history is None:
            return []

        if include_provenance:
            return self._history.copy()
        else:
            # Return history without provenance information
            return [{"func": op["func"], "args": op["args"]} for op in self._history]

    def export_history(self, format="json"):
        """
        Export the operation history in a serializable format.

        Parameters
        ----------
        format : str, optional
            Export format: 'json', 'yaml', or 'python' (default: 'json')

        Returns
        -------
        str
            Serialized history

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> print(ds.export_history('python'))
        ds = DummyDataset()
        ds.add_dim(name='time', size=10)
        """
        history = self.get_history()

        if format == "json":
            return json.dumps(history, indent=2)
        elif format == "yaml":
            return yaml.dump(history, default_flow_style=False)
        elif format == "python":
            lines = []
            for op in history:
                if op["func"] == "__init__":
                    lines.append("ds = DummyDataset()")
                else:
                    args_str = ", ".join(f"{k}={repr(v)}" for k, v in op["args"].items())
                    lines.append(f"ds.{op['func']}({args_str})")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unknown format: {format}. Use 'json', 'yaml', or 'python'")

    @classmethod
    def replay_history(cls, history):
        """
        Replay a sequence of operations to recreate a dataset.

        Parameters
        ----------
        history : list of dict or str
            History to replay. Can be a list of operations or a JSON/YAML string.

        Returns
        -------
        DummyDataset
            New dataset with operations replayed

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> history = ds.get_history()
        >>> new_ds = DummyDataset.replay_history(history)
        """
        # Parse history if it's a string
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except json.JSONDecodeError:
                history = yaml.safe_load(history)

        # Create new dataset without recording
        ds = cls(_record_history=False)

        # Replay operations (skip __init__)
        for op in history:
            if op["func"] == "__init__":
                continue

            func = getattr(ds, op["func"], None)
            if func and callable(func):
                func(**op["args"])

        return ds

    def reset_history(self):
        """
        Reset the operation history and provenance tracking.

        This is useful after capturing an initial dataset state (e.g., from xarray)
        when you want to track only subsequent modifications without the initial
        construction operations.

        Examples
        --------
        >>> # Capture initial state from xarray
        >>> ds = DummyDataset.from_xarray(xr_dataset)
        >>> # Reset to start tracking only new changes
        >>> ds.reset_history()
        >>> # Now modifications are tracked from this point
        >>> ds.assign_attrs(institution="DKRZ")
        >>> # History only shows changes after reset
        >>> print(ds.visualize_history())
        """
        self._history = []
        self._record_operation("__init__", {})

    def visualize_history(self, format="text", **kwargs):
        """
        Visualize the operation history.

        Parameters
        ----------
        format : str, optional
            Visualization format: 'text', 'dot', 'mermaid' (default: 'text')
        **kwargs
            Additional arguments for specific formats:
            - show_args : bool - Show operation arguments (default: True)
            - compact : bool - Use compact representation (default: False)

        Returns
        -------
        str
            Formatted visualization string

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"])
        >>> print(ds.visualize_history())
        Dataset Construction History
        ============================
        1. __init__()
        2. add_dim(name='time', size=10)
        3. add_coord(name='time', dims=['time'])

        >>> print(ds.visualize_history(format='dot'))
        digraph dataset_history { ... }
        """
        history = self.get_history()
        show_args = kwargs.get("show_args", True)
        compact = kwargs.get("compact", False)

        if format == "text":
            return self._visualize_text(history, show_args, compact)
        elif format == "dot":
            return self._visualize_dot(history, show_args)
        elif format == "mermaid":
            return self._visualize_mermaid(history, show_args)
        else:
            raise ValueError(f"Unknown format: {format}. Use 'text', 'dot', or 'mermaid'")

    def _visualize_text(self, history, show_args=True, compact=False):
        """Create a text-based visualization of the history."""
        if not history:
            return "No operations recorded"

        if compact:
            lines = []
            for i, op in enumerate(history, 1):
                if show_args and op["args"]:
                    args_str = ", ".join(f"{k}={repr(v)}" for k, v in op["args"].items())
                    lines.append(f"{i}. {op['func']}({args_str})")
                else:
                    lines.append(f"{i}. {op['func']}()")
            return "\n".join(lines)
        else:
            lines = ["Dataset Construction History", "=" * 28, ""]

            for i, op in enumerate(history, 1):
                if show_args and op["args"]:
                    args_str = ", ".join(f"{k}={repr(v)}" for k, v in op["args"].items())
                    lines.append(f"{i}. {op['func']}({args_str})")
                else:
                    lines.append(f"{i}. {op['func']}()")

            # Add summary
            lines.append("")
            lines.append("Summary:")
            lines.append(f"  Total operations: {len(history)}")

            # Count operation types
            op_counts = {}
            for op in history:
                op_counts[op["func"]] = op_counts.get(op["func"], 0) + 1

            lines.append("  Operation breakdown:")
            for func, count in sorted(op_counts.items()):
                lines.append(f"    {func}: {count}")

            return "\n".join(lines)

    def _visualize_dot(self, history, show_args=True):
        """Create a Graphviz DOT format visualization."""
        lines = [
            "digraph dataset_history {",
            "  rankdir=TB;",
            "  node [shape=box, style=rounded];",
            "",
        ]

        # Create nodes for each operation
        for i, op in enumerate(history):
            label = op["func"]
            if show_args and op["args"]:
                args_str = "\\n".join(f"{k}={repr(v)}" for k, v in list(op["args"].items())[:3])
                if len(op["args"]) > 3:
                    args_str += "\\n..."
                label = f"{label}\\n{args_str}"

            # Color code by operation type
            color = self._get_operation_color(op["func"])
            lines.append(f'  op{i} [label="{label}", fillcolor="{color}", style=filled];')

        # Create edges
        for i in range(len(history) - 1):
            lines.append(f"  op{i} -> op{i+1};")

        lines.append("}")
        return "\n".join(lines)

    def _visualize_mermaid(self, history, show_args=True):
        """Create a Mermaid diagram visualization."""
        lines = ["graph TD"]

        # Create nodes for each operation
        for i, op in enumerate(history):
            label = op["func"]
            if show_args and op["args"]:
                args_str = "<br/>".join(f"{k}={repr(v)}" for k, v in list(op["args"].items())[:2])
                if len(op["args"]) > 2:
                    args_str += "<br/>..."
                label = f"{label}<br/>{args_str}"

            # Use different shapes for different operations
            if op["func"] == "__init__":
                lines.append(f'  op{i}["{label}"]')
            elif op["func"].startswith("add_"):
                lines.append(f'  op{i}("{label}")')
            else:
                lines.append(f'  op{i}["{label}"]')

        # Create edges
        for i in range(len(history) - 1):
            lines.append(f"  op{i} --> op{i+1}")

        return "\n".join(lines)

    def _get_operation_color(self, func_name):
        """Get color for operation type."""
        color_map = {
            "__init__": "lightblue",
            "add_dim": "lightgreen",
            "add_coord": "lightyellow",
            "add_variable": "lightcoral",
            "assign_attrs": "lavender",
            "populate_with_random_data": "lightpink",
        }
        return color_map.get(func_name, "lightgray")

    def get_provenance(self, operation_index=None):
        """
        Get provenance information showing what changed in each operation.

        Parameters
        ----------
        operation_index : int, optional
            If provided, return provenance for a specific operation.
            Otherwise, return provenance for all operations.

        Returns
        -------
        dict or list of dict
            Provenance information showing changes

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.assign_attrs(units='degC')
        >>> ds.assign_attrs(units='K')  # Overwrites previous value
        >>> prov = ds.get_provenance()
        >>> prov[2]['provenance']['modified']['units']
        {'before': 'degC', 'after': 'K'}
        """
        history = self.get_history(include_provenance=True)

        if operation_index is not None:
            if 0 <= operation_index < len(history):
                return history[operation_index].get("provenance", {})
            else:
                raise IndexError(f"Operation index {operation_index} out of range")

        # Return all provenance information
        return [
            {
                "index": i,
                "func": op["func"],
                "provenance": op.get("provenance", {}),
            }
            for i, op in enumerate(history)
            if "provenance" in op
        ]

    def visualize_provenance(self, compact=False):
        """
        Visualize provenance information showing what changed.

        Parameters
        ----------
        compact : bool, optional
            Use compact representation (default: False)

        Returns
        -------
        str
            Formatted provenance visualization

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.assign_attrs(units='degC', title='Test')
        >>> ds.assign_attrs(units='K')  # Overwrites units
        >>> print(ds.visualize_provenance())
        Provenance: Dataset Changes
        ============================

        Operation 1: assign_attrs
          Modified attributes:
            units: None → 'degC'
            title: None → 'Test'

        Operation 2: assign_attrs
          Modified attributes:
            units: 'degC' → 'K'
        """
        history = self.get_history(include_provenance=True)

        if compact:
            lines = []
            for i, op in enumerate(history):
                if "provenance" not in op:
                    continue
                prov = op["provenance"]
                changes = []
                if "renamed" in prov:
                    for old, new in prov["renamed"].items():
                        changes.append(f"renamed: {old} → {new}")
                if "added" in prov:
                    changes.append(f"added: {', '.join(prov['added'])}")
                if "removed" in prov:
                    changes.append(f"removed: {', '.join(prov['removed'])}")
                if "modified" in prov:
                    for key, change in prov["modified"].items():
                        if isinstance(change, dict) and "before" in change:
                            changes.append(f"{key}: {change['before']} → {change['after']}")
                        else:
                            changes.append(f"{key}: modified")
                if changes:
                    lines.append(f"{i}. {op['func']}: {'; '.join(changes)}")
            return "\n".join(lines) if lines else "No changes recorded"
        else:
            lines = ["Provenance: Dataset Changes", "=" * 28, ""]

            has_changes = False
            for i, op in enumerate(history):
                if "provenance" not in op:
                    continue

                has_changes = True
                prov = op["provenance"]
                lines.append(f"Operation {i}: {op['func']}")

                if "renamed" in prov:
                    lines.append("  Renamed:")
                    for old, new in prov["renamed"].items():
                        lines.append(f"    {old} → {new}")

                if "added" in prov:
                    lines.append(f"  Added: {', '.join(prov['added'])}")

                if "removed" in prov:
                    lines.append(f"  Removed: {', '.join(prov['removed'])}")

                if "modified" in prov:
                    lines.append("  Modified:")
                    for key, change in prov["modified"].items():
                        if isinstance(change, dict) and "before" in change:
                            before = (
                                repr(change["before"]) if change["before"] is not None else "None"
                            )
                            after = repr(change["after"])
                            lines.append(f"    {key}: {before} → {after}")
                        else:
                            # Nested changes (e.g., for coords/variables)
                            lines.append(f"    {key}:")
                            for subkey, subchange in change.items():
                                before = repr(subchange["before"])
                                after = repr(subchange["after"])
                                lines.append(f"      {subkey}: {before} → {after}")

                lines.append("")

            if not has_changes:
                return "No changes recorded"

            return "\n".join(lines)

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------

    def set_global_attrs(self, **kwargs):
        """
        Set or update global dataset attributes.

        Parameters
        ----------
        **kwargs
            Attribute key-value pairs

        Examples
        --------
        >>> ds.set_global_attrs(title="My Dataset", institution="DKRZ")
        """
        self.attrs.update(kwargs)

    def assign_attrs(self, **kwargs):
        """
        Assign new global attributes to this dataset (xarray-compatible API).

        This method updates the dataset's global attributes dictionary in-place
        and returns self for method chaining, matching xarray's behavior.

        Parameters
        ----------
        **kwargs
            Attribute key-value pairs to assign

        Returns
        -------
        DummyDataset
            Returns self for method chaining

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.assign_attrs(title="My Dataset", institution="DKRZ")
        >>> ds.assign_attrs(experiment="historical")

        Notes
        -----
        This is equivalent to `set_global_attrs()` but follows xarray's API
        convention and returns self for method chaining.
        """
        # Capture provenance: track what changed
        provenance = {"modified": {}}
        for key, new_value in kwargs.items():
            old_value = self.attrs.get(key)
            if old_value != new_value:
                provenance["modified"][key] = {"before": old_value, "after": new_value}

        self._record_operation(
            "assign_attrs", kwargs, provenance if provenance["modified"] else None
        )
        self.attrs.update(kwargs)
        return self

    def add_dim(self, name, size):
        """
        Add a dimension with a specific size.

        Parameters
        ----------
        name : str
            Dimension name
        size : int
            Dimension size
        """
        # Capture provenance
        provenance = {}
        if name in self.dims:
            # Dimension already exists - this is a modification
            provenance["modified"] = {name: {"before": self.dims[name], "after": size}}
        else:
            # New dimension
            provenance["added"] = [name]

        self._record_operation("add_dim", {"name": name, "size": size}, provenance)
        self.dims[name] = size

    def add_coord(self, name, dims=None, attrs=None, data=None, encoding=None):
        """
        Add a coordinate variable.

        Parameters
        ----------
        name : str
            Coordinate name
        dims : list of str, optional
            List of dimension names (inferred from data if not provided)
        attrs : dict, optional
            Metadata attributes
        data : array-like, optional
            Coordinate data
        encoding : dict, optional
            Encoding parameters
        """
        # Record operation (don't store actual data)
        args = {"name": name}
        if dims is not None:
            args["dims"] = dims
        if attrs:
            args["attrs"] = attrs
        if data is not None:
            args["data"] = "<data>"
        if encoding:
            args["encoding"] = encoding

        # Capture provenance
        provenance = {}
        if name in self.coords:
            # Coordinate already exists - track what changed
            old_coord = self.coords[name]
            changes = {}
            if dims != old_coord.dims:
                changes["dims"] = {"before": old_coord.dims, "after": dims}
            if attrs and attrs != old_coord.attrs:
                changes["attrs"] = {"before": old_coord.attrs.copy(), "after": attrs}
            if changes:
                provenance["modified"] = {name: changes}
        else:
            provenance["added"] = [name]

        self._record_operation("add_coord", args, provenance)

        arr = DummyArray(dims, attrs, data, encoding, _record_history=False)
        self._infer_and_register_dims(arr)
        self.coords[name] = arr

    def add_variable(self, name, dims=None, attrs=None, data=None, encoding=None):
        """
        Add a data variable.

        Parameters
        ----------
        name : str
            Variable name
        dims : list of str, optional
            List of dimension names (inferred from data if not provided)
        attrs : dict, optional
            Metadata attributes
        data : array-like, optional
            Variable data
        encoding : dict, optional
            Encoding parameters (dtype, chunks, compressor, fill_value, etc.)
        """
        # Record operation (don't store actual data)
        args = {"name": name}
        if dims is not None:
            args["dims"] = dims
        if attrs:
            args["attrs"] = attrs
        if data is not None:
            args["data"] = "<data>"
        if encoding:
            args["encoding"] = encoding

        # Capture provenance
        provenance = {}
        if name in self.variables:
            # Variable already exists - track what changed
            old_var = self.variables[name]
            changes = {}
            if dims != old_var.dims:
                changes["dims"] = {"before": old_var.dims, "after": dims}
            if attrs and attrs != old_var.attrs:
                changes["attrs"] = {"before": old_var.attrs.copy(), "after": attrs}
            if changes:
                provenance["modified"] = {name: changes}
        else:
            provenance["added"] = [name]

        self._record_operation("add_variable", args, provenance)

        arr = DummyArray(dims, attrs, data, encoding, _record_history=False)
        self._infer_and_register_dims(arr)
        self.variables[name] = arr

    def rename_dims(self, dims_dict=None, **dims):
        """
        Rename dimensions (xarray-compatible API).

        Parameters
        ----------
        dims_dict : dict-like, optional
            Dictionary whose keys are current dimension names and whose
            values are the desired names.
        **dims : optional
            Keyword form of dims_dict.
            One of dims_dict or dims must be provided.

        Returns
        -------
        DummyDataset
            Returns self for method chaining

        Raises
        ------
        KeyError
            If a dimension doesn't exist
        ValueError
            If a new name already exists

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_dim("lat", 64)
        >>> ds.rename_dims({"time": "t", "lat": "latitude"})
        >>> # Or using keyword arguments:
        >>> ds.rename_dims(time="t", lat="latitude")
        """
        # Merge dims_dict and **dims
        name_dict = {}
        if dims_dict is not None:
            name_dict.update(dims_dict)
        name_dict.update(dims)

        if not name_dict:
            raise ValueError("Either dims_dict or keyword arguments must be provided")

        # Validate all renames first
        for old_name, new_name in name_dict.items():
            if old_name not in self.dims:
                raise KeyError(f"Dimension '{old_name}' does not exist")
            if new_name in self.dims and new_name != old_name:
                raise ValueError(f"Dimension '{new_name}' already exists")

        # Capture provenance
        provenance = {
            "renamed": name_dict.copy(),
            "removed": list(name_dict.keys()),
            "added": list(name_dict.values()),
        }

        self._record_operation("rename_dims", {"dims_dict": name_dict}, provenance)

        # Perform all renames
        for old_name, new_name in name_dict.items():
            if old_name != new_name:
                self.dims[new_name] = self.dims.pop(old_name)

                # Update dimension references in coords and variables
                for coord in self.coords.values():
                    if coord.dims:
                        coord.dims = [new_name if d == old_name else d for d in coord.dims]
                for var in self.variables.values():
                    if var.dims:
                        var.dims = [new_name if d == old_name else d for d in var.dims]

        return self

    def rename_vars(self, name_dict=None, **names):
        """
        Rename variables (xarray-compatible API).

        Parameters
        ----------
        name_dict : dict-like, optional
            Dictionary whose keys are current variable names and whose
            values are the desired names.
        **names : optional
            Keyword form of name_dict.
            One of name_dict or names must be provided.

        Returns
        -------
        DummyDataset
            Returns self for method chaining

        Raises
        ------
        KeyError
            If a variable doesn't exist
        ValueError
            If a new name already exists

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_variable("temperature", dims=["time"])
        >>> ds.rename_vars({"temperature": "temp"})
        >>> # Or using keyword arguments:
        >>> ds.rename_vars(temperature="temp")
        """
        # Merge name_dict and **names
        rename_dict = {}
        if name_dict is not None:
            rename_dict.update(name_dict)
        rename_dict.update(names)

        if not rename_dict:
            raise ValueError("Either name_dict or keyword arguments must be provided")

        # Validate all renames first
        for old_name, new_name in rename_dict.items():
            if old_name not in self.variables:
                raise KeyError(f"Variable '{old_name}' does not exist")
            if new_name in self.variables and new_name != old_name:
                raise ValueError(f"Variable '{new_name}' already exists")

        # Capture provenance
        provenance = {
            "renamed": rename_dict.copy(),
            "removed": list(rename_dict.keys()),
            "added": list(rename_dict.values()),
        }

        self._record_operation("rename_vars", {"name_dict": rename_dict}, provenance)

        # Perform all renames
        for old_name, new_name in rename_dict.items():
            if old_name != new_name:
                self.variables[new_name] = self.variables.pop(old_name)

        return self

    def rename(self, name_dict=None, **names):
        """
        Rename variables, coordinates, and dimensions (xarray-compatible API).

        This method can rename any combination of variables, coordinates, and dimensions.

        Parameters
        ----------
        name_dict : dict-like, optional
            Dictionary whose keys are current names (variables, coordinates, or dimensions)
            and whose values are the desired names.
        **names : optional
            Keyword form of name_dict.
            One of name_dict or names must be provided.

        Returns
        -------
        DummyDataset
            Returns self for method chaining

        Raises
        ------
        KeyError
            If a name doesn't exist
        ValueError
            If a new name already exists

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"])
        >>> ds.add_variable("temperature", dims=["time"])
        >>> # Rename multiple items at once
        >>> ds.rename({"time": "t", "temperature": "temp"})
        >>> # Or using keyword arguments:
        >>> ds.rename(time="t", temperature="temp")
        """
        # Merge name_dict and **names
        rename_dict = {}
        if name_dict is not None:
            rename_dict.update(name_dict)
        rename_dict.update(names)

        if not rename_dict:
            raise ValueError("Either name_dict or keyword arguments must be provided")

        # Categorize renames
        dim_renames = {}
        coord_renames = {}
        var_renames = {}

        for old_name, new_name in rename_dict.items():
            if old_name in self.dims:
                dim_renames[old_name] = new_name
            if old_name in self.coords:
                coord_renames[old_name] = new_name
            if old_name in self.variables:
                var_renames[old_name] = new_name

            # Check if name exists anywhere
            if (
                old_name not in self.dims
                and old_name not in self.coords
                and old_name not in self.variables
            ):
                raise KeyError(
                    f"'{old_name}' does not exist in dimensions, coordinates, or variables"
                )

        # Capture provenance
        provenance = {
            "renamed": rename_dict.copy(),
            "removed": list(rename_dict.keys()),
            "added": list(rename_dict.values()),
        }

        self._record_operation("rename", {"name_dict": rename_dict}, provenance)

        # Perform renames in order: dimensions first (affects coords/vars), then coords, then vars
        if dim_renames:
            for old_name, new_name in dim_renames.items():
                if old_name != new_name and old_name in self.dims:
                    self.dims[new_name] = self.dims.pop(old_name)
                    # Update dimension references
                    for coord in self.coords.values():
                        if coord.dims:
                            coord.dims = [new_name if d == old_name else d for d in coord.dims]
                    for var in self.variables.values():
                        if var.dims:
                            var.dims = [new_name if d == old_name else d for d in var.dims]

        if coord_renames:
            for old_name, new_name in coord_renames.items():
                if old_name != new_name and old_name in self.coords:
                    self.coords[new_name] = self.coords.pop(old_name)

        if var_renames:
            for old_name, new_name in var_renames.items():
                if old_name != new_name and old_name in self.variables:
                    self.variables[new_name] = self.variables.pop(old_name)

        return self

    # ------------------------------------------------------------
    # CF Compliance and Axis Detection
    # ------------------------------------------------------------

    def infer_axis(self, coord_name=None):
        """
        Infer axis attribute (X/Y/Z/T) for coordinates based on CF conventions.

        Uses coordinate names, standard_name attributes, units, and dimension
        patterns to automatically detect axis types.

        Parameters
        ----------
        coord_name : str, optional
            Specific coordinate to infer axis for. If None, infers for all coordinates.

        Returns
        -------
        dict
            Dictionary mapping coordinate names to inferred axis values ('X', 'Y', 'Z', 'T')

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_dim("lat", 64)
        >>> ds.add_dim("lon", 128)
        >>> ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        >>> ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        >>> ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
        >>> axes = ds.infer_axis()
        >>> # Returns: {'time': 'T', 'lat': 'Y', 'lon': 'X'}
        """
        axes = {}
        coords_to_check = [coord_name] if coord_name else list(self.coords.keys())

        for name in coords_to_check:
            if name not in self.coords:
                continue

            coord = self.coords[name]
            axis = self._detect_axis_type(name, coord)
            if axis:
                axes[name] = axis

        return axes

    def _detect_axis_type(self, name, coord):
        """
        Detect axis type for a coordinate based on CF conventions.

        Parameters
        ----------
        name : str
            Coordinate name
        coord : DummyArray
            Coordinate object

        Returns
        -------
        str or None
            Axis type ('X', 'Y', 'Z', 'T') or None if cannot be determined
        """
        # Check if axis already set
        if coord.attrs.get("axis"):
            return coord.attrs["axis"]

        # Check standard_name (CF convention)
        standard_name = coord.attrs.get("standard_name", "").lower()
        standard_name_map = {
            "longitude": "X",
            "projection_x_coordinate": "X",
            "grid_longitude": "X",
            "latitude": "Y",
            "projection_y_coordinate": "Y",
            "grid_latitude": "Y",
            "altitude": "Z",
            "height": "Z",
            "depth": "Z",
            "air_pressure": "Z",
            "model_level_number": "Z",
            "time": "T",
        }
        if standard_name in standard_name_map:
            return standard_name_map[standard_name]

        # Check units (CF convention)
        units = coord.attrs.get("units", "").lower()

        # Time axis patterns
        time_patterns = ["since", "days", "hours", "minutes", "seconds"]
        if any(pattern in units for pattern in time_patterns):
            return "T"

        # Longitude patterns
        if units in ["degrees_east", "degree_east", "degreee", "degreese"]:
            return "X"

        # Latitude patterns
        if units in ["degrees_north", "degree_north", "degreen", "degreesn"]:
            return "Y"

        # Vertical coordinate patterns
        vertical_units = ["pa", "hpa", "mbar", "bar", "m", "km", "level", "sigma", "eta"]
        if any(units.startswith(u) for u in vertical_units):
            return "Z"

        # Check coordinate name patterns (common conventions)
        name_lower = name.lower()

        # X-axis patterns
        x_patterns = ["lon", "longitude", "x", "i", "ni", "xc"]
        if any(name_lower.startswith(p) or name_lower == p for p in x_patterns):
            return "X"

        # Y-axis patterns
        y_patterns = ["lat", "latitude", "y", "j", "nj", "yc"]
        if any(name_lower.startswith(p) or name_lower == p for p in y_patterns):
            return "Y"

        # Z-axis patterns
        z_patterns = ["lev", "level", "plev", "height", "depth", "alt", "z", "k", "nk"]
        if any(name_lower.startswith(p) or name_lower == p for p in z_patterns):
            return "Z"

        # T-axis patterns
        t_patterns = ["time", "t", "date"]
        if any(name_lower.startswith(p) or name_lower == p for p in t_patterns):
            return "T"

        return None

    def set_axis_attributes(self, inferred_only=False):
        """
        Set axis attributes on coordinates based on inferred axis types.

        This modifies coordinate attributes in-place to add 'axis' attributes
        following CF conventions.

        Parameters
        ----------
        inferred_only : bool, default False
            If True, only set axis for coordinates that don't already have one.
            If False, overwrite existing axis attributes with inferred values.

        Returns
        -------
        dict
            Dictionary of coordinate names and their assigned axis values

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        >>> ds.set_axis_attributes()
        >>> print(ds.coords["time"].attrs["axis"])
        T
        """
        assigned = {}

        for coord_name, coord in self.coords.items():
            # Check if we should skip this coordinate
            if inferred_only and "axis" in coord.attrs:
                continue

            # Temporarily remove axis attribute to force re-inference
            existing_axis = coord.attrs.pop("axis", None)

            # Infer axis for this coordinate
            axis = self._detect_axis_type(coord_name, coord)

            if axis:
                # Set the inferred axis attribute
                coord.attrs["axis"] = axis
                assigned[coord_name] = axis
            elif existing_axis:
                # Restore existing axis if we couldn't infer a new one
                coord.attrs["axis"] = existing_axis

        return assigned

    def get_axis_coordinates(self, axis):
        """
        Get all coordinates with a specific axis attribute.

        Parameters
        ----------
        axis : str
            Axis type to search for ('X', 'Y', 'Z', 'T')

        Returns
        -------
        list
            List of coordinate names with the specified axis

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})
        >>> ds.add_coord("lat", dims=["lat"], attrs={"axis": "Y"})
        >>> x_coords = ds.get_axis_coordinates("X")
        >>> # Returns: ['lon']
        """
        coords = []
        for name, coord in self.coords.items():
            if coord.attrs.get("axis") == axis:
                coords.append(name)
        return coords

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    def validate(self, strict_coords=False):
        """
        Validate the entire dataset structure.

        Parameters
        ----------
        strict_coords : bool, default False
            If True, require that all variable dimensions have corresponding coordinates

        Raises
        ------
        ValueError
            If validation fails
        """
        errors = []

        # 1. Dimensions must be known
        all_dims = set(self.dims.keys())

        for name, arr in {**self.coords, **self.variables}.items():
            if arr.dims is None:
                continue
            for d in arr.dims:
                if d not in all_dims:
                    errors.append(f"{name}: Unknown dimension '{d}'.")

        # 2. Data shapes must match dims
        for name, arr in {**self.coords, **self.variables}.items():
            if arr.data is not None and arr.dims is not None:
                shape = np.asarray(arr.data).shape
                dim_sizes = [self.dims[d] for d in arr.dims]
                if tuple(dim_sizes) != shape:
                    errors.append(f"{name}: Data shape {shape} does not match dims {dim_sizes}.")

        # 3. Variables reference coords?
        if strict_coords:
            coord_names = set(self.coords.keys())
            for name, arr in self.variables.items():
                if arr.dims:
                    for d in arr.dims:
                        if d not in coord_names:
                            errors.append(f"{name}: Missing coordinate for dimension '{d}'.")

        if errors:
            raise ValueError("Dataset validation failed:\n" + "\n".join(errors))

    def validate_cf(self, strict=False):
        """
        Validate dataset against CF conventions.

        Checks for common CF compliance issues like missing axis attributes,
        invalid units, missing standard_name, etc.

        Parameters
        ----------
        strict : bool, default False
            If True, raise ValueError on any CF violation.
            If False, return a list of warnings/errors.

        Returns
        -------
        dict
            Dictionary with 'errors' and 'warnings' lists

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"])
        >>> result = ds.validate_cf()
        >>> print(result['warnings'])
        ['time: Missing axis attribute', 'time: Missing units attribute']
        """
        errors = []
        warnings = []

        # Check coordinates for axis attributes
        for name, coord in self.coords.items():
            # Check for axis attribute
            if "axis" not in coord.attrs:
                inferred = self.infer_axis(name)
                if name in inferred:
                    warnings.append(
                        f"{name}: Missing 'axis' attribute (can be inferred as '{inferred[name]}')"
                    )
                else:
                    warnings.append(f"{name}: Missing 'axis' attribute (cannot infer)")

            # Check for units
            if "units" not in coord.attrs:
                warnings.append(f"{name}: Missing 'units' attribute")

            # Check for standard_name on coordinates
            if "standard_name" not in coord.attrs:
                warnings.append(f"{name}: Missing 'standard_name' attribute")

        # Check variables for required attributes
        for name, var in self.variables.items():
            # Check for units
            if "units" not in var.attrs:
                warnings.append(f"{name}: Variable missing 'units' attribute")

            # Check for long_name or standard_name
            if "long_name" not in var.attrs and "standard_name" not in var.attrs:
                warnings.append(f"{name}: Variable missing both 'long_name' and 'standard_name'")

        # Check global attributes
        required_global = ["Conventions"]
        for attr in required_global:
            if attr not in self.attrs:
                warnings.append(f"Missing required global attribute: '{attr}'")

        # Check for CF Conventions version
        if "Conventions" in self.attrs:
            conventions = self.attrs["Conventions"]
            if not any(cf in conventions for cf in ["CF-", "cf-"]):
                warnings.append(f"Conventions attribute '{conventions}' does not reference CF")

        # Check dimension ordering (CF recommends T, Z, Y, X)
        for name, var in self.variables.items():
            if var.dims and len(var.dims) > 1:
                # Get axis types for dimensions
                dim_axes = []
                for dim in var.dims:
                    if dim in self.coords:
                        axis = self.coords[dim].attrs.get("axis")
                        if axis:
                            dim_axes.append(axis)

                # Check if order is T, Z, Y, X
                expected_order = ["T", "Z", "Y", "X"]
                actual_order = [a for a in dim_axes if a in expected_order]
                sorted_order = sorted(actual_order, key=lambda x: expected_order.index(x))

                if actual_order != sorted_order:
                    warnings.append(
                        f"{name}: Dimension order {actual_order} does not follow "
                        f"CF recommendation (T, Z, Y, X)"
                    )

        result = {"errors": errors, "warnings": warnings}

        if strict and (errors or warnings):
            all_issues = errors + warnings
            raise ValueError("CF validation failed:\n" + "\n".join(all_issues))

        return result

    # ------------------------------------------------------------
    # Internal dimension inference
    # ------------------------------------------------------------

    def _infer_and_register_dims(self, arr):
        """
        Infer dimension sizes from data and register them.

        Parameters
        ----------
        arr : DummyArray
            Array to infer dimensions from

        Raises
        ------
        ValueError
            If dimension sizes conflict
        """
        inferred = arr.infer_dims_from_data()

        for dim, size in inferred.items():
            if dim in self.dims:
                if self.dims[dim] != size:
                    raise ValueError(
                        f"Dimension mismatch for '{dim}': existing={self.dims[dim]} new={size}"
                    )
            else:
                self.dims[dim] = size

    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------

    def to_dict(self):
        """
        Export dataset structure to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the dataset
        """
        return {
            "dimensions": self.dims,
            "coordinates": {k: v.to_dict() for k, v in self.coords.items()},
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "attrs": self.attrs,
        }

    def to_json(self, **kwargs):
        """
        Export dataset structure to JSON string.

        Parameters
        ----------
        **kwargs
            Additional arguments passed to json.dumps

        Returns
        -------
        str
            JSON representation
        """
        return json.dumps(self.to_dict(), indent=2, **kwargs)

    def to_yaml(self):
        """
        Export dataset structure to YAML string.

        Returns
        -------
        str
            YAML representation
        """
        return yaml.dump(self.to_dict(), sort_keys=False)

    def save_yaml(self, path):
        """
        Save dataset specification to a YAML file.

        Parameters
        ----------
        path : str
            Output file path
        """
        with open(path, "w") as f:
            f.write(self.to_yaml())

    @classmethod
    def load_yaml(cls, path):
        """
        Load dataset specification from a YAML file.

        Parameters
        ----------
        path : str
            Input file path

        Returns
        -------
        DummyDataset
            Loaded dataset (without data arrays)
        """
        with open(path) as f:
            spec = yaml.safe_load(f)

        ds = cls()

        ds.dims.update(spec.get("dimensions", {}))

        for name, info in spec.get("coordinates", {}).items():
            ds.coords[name] = DummyArray(
                dims=info["dims"], attrs=info["attrs"], data=None, encoding=info.get("encoding", {})
            )

        for name, info in spec.get("variables", {}).items():
            ds.variables[name] = DummyArray(
                dims=info["dims"], attrs=info["attrs"], data=None, encoding=info.get("encoding", {})
            )

        ds.attrs.update(spec.get("attrs", {}))

        return ds

    @classmethod
    def from_xarray(cls, xr_dataset, include_data=False):
        """
        Create a DummyDataset from an existing xarray.Dataset.

        This captures all metadata (dimensions, coordinates, variables, attributes,
        and encoding) from an xarray.Dataset without the actual data arrays
        (unless include_data=True).

        Parameters
        ----------
        xr_dataset : xarray.Dataset
            The xarray Dataset to extract metadata from
        include_data : bool, default False
            If True, include the actual data arrays. If False, only capture
            metadata structure.

        Returns
        -------
        DummyDataset
            A new DummyDataset with the structure and metadata from xr_dataset

        Examples
        --------
        >>> import xarray as xr
        >>> import numpy as np
        >>> xr_ds = xr.Dataset({
        ...     "temperature": (["time", "lat"], np.random.rand(10, 5))
        ... })
        >>> dummy_ds = DummyDataset.from_xarray(xr_ds)
        >>> print(dummy_ds.dims)
        {'time': 10, 'lat': 5}
        """
        ds = cls()

        # Copy global attributes
        ds.attrs.update(dict(xr_dataset.attrs))

        # Extract dimensions
        for dim_name, dim_size in xr_dataset.sizes.items():
            ds.dims[dim_name] = dim_size

        # Extract coordinates
        for coord_name, coord_var in xr_dataset.coords.items():
            ds.coords[coord_name] = DummyArray(
                dims=list(coord_var.dims),
                attrs=dict(coord_var.attrs),
                data=coord_var.values if include_data else None,
                encoding=dict(coord_var.encoding) if hasattr(coord_var, "encoding") else {},
            )

        # Extract data variables
        for var_name, var in xr_dataset.data_vars.items():
            ds.variables[var_name] = DummyArray(
                dims=list(var.dims),
                attrs=dict(var.attrs),
                data=var.values if include_data else None,
                encoding=dict(var.encoding) if hasattr(var, "encoding") else {},
            )

        return ds

    def populate_with_random_data(self, seed=None):
        """
        Populate all variables and coordinates with random but meaningful data.

        This method generates random data based on variable metadata (units,
        standard_name, etc.) to create realistic-looking test datasets.

        Parameters
        ----------
        seed : int, optional
            Random seed for reproducibility

        Returns
        -------
        self
            Returns self for method chaining

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_dim("lat", 5)
        >>> ds.add_coord("time", ["time"], attrs={"units": "days"})
        >>> ds.add_variable("temperature", ["time", "lat"],
        ...                 attrs={"units": "K"})
        >>> ds.populate_with_random_data(seed=42)
        >>> print(ds.coords["time"].data)
        [0 1 2 3 4 5 6 7 8 9]
        """
        if seed is not None:
            np.random.seed(seed)

        # Populate coordinates
        for coord_name, coord_array in self.coords.items():
            if coord_array.data is None:
                coord_array.data = self._generate_coordinate_data(coord_name, coord_array)

        # Populate variables
        for var_name, var_array in self.variables.items():
            if var_array.data is None:
                var_array.data = self._generate_variable_data(var_name, var_array)

        return self

    def _generate_coordinate_data(self, name, array):
        """Generate meaningful coordinate data based on metadata."""
        shape = tuple(self.dims[d] for d in array.dims)
        size = shape[0] if shape else 1

        # Check standard_name or units for hints
        standard_name = array.attrs.get("standard_name", "").lower()
        units = array.attrs.get("units", "").lower()

        # Time coordinates
        if "time" in name.lower() or "time" in standard_name:
            return np.arange(size)

        # Latitude coordinates
        if "lat" in name.lower() or "latitude" in standard_name:
            return np.linspace(-90, 90, size)

        # Longitude coordinates
        if "lon" in name.lower() or "longitude" in standard_name:
            return np.linspace(-180, 180, size)

        # Vertical levels (pressure, height, etc.)
        if any(x in name.lower() for x in ["lev", "level", "plev", "height", "depth"]):
            if "pressure" in units or "hpa" in units or "pa" in units:
                # Pressure levels (high to low)
                return np.linspace(1000, 100, size)
            else:
                # Generic levels
                return np.arange(size)

        # Default: sequential integers
        return np.arange(size)

    def _generate_variable_data(self, name, array):
        """Generate meaningful variable data based on metadata."""
        shape = tuple(self.dims[d] for d in array.dims)

        # Get metadata hints
        standard_name = array.attrs.get("standard_name", "").lower()
        units = array.attrs.get("units", "").lower()
        long_name = array.attrs.get("long_name", "").lower()

        # Temperature variables
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["temperature", "temp", "tas", "ts"]
        ):
            if "k" == units or "kelvin" in units:
                # Temperature in Kelvin (250-310K range)
                return np.random.uniform(250, 310, shape)
            elif "c" == units or "celsius" in units or "degc" in units:
                # Temperature in Celsius (-30 to 40C range)
                return np.random.uniform(-30, 40, shape)
            else:
                return np.random.uniform(250, 310, shape)

        # Pressure variables (check before precipitation to avoid "pr" conflict)
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["pressure", "pres", "psl"]
        ):
            if "sea_level" in standard_name or "msl" in name.lower() or "psl" in name.lower():
                # Sea level pressure (980-1040 hPa)
                return np.random.uniform(98000, 104000, shape)
            else:
                # Generic pressure
                return np.random.uniform(50000, 105000, shape)

        # Precipitation variables
        if (
            any(
                x in standard_name or x in name.lower() or x in long_name
                for x in ["precipitation", "precip", "rain"]
            )
            or name.lower() == "pr"
        ):
            # Precipitation (always positive, skewed distribution)
            return np.random.exponential(0.001, shape)

        # Wind variables
        if any(
            x in standard_name or x in name.lower() or x in long_name for x in ["wind", "velocity"]
        ):
            # Wind speed (0-30 m/s, can be negative for components)
            if any(x in name.lower() for x in ["u", "zonal", "eastward"]):
                return np.random.uniform(-20, 20, shape)
            elif any(x in name.lower() for x in ["v", "meridional", "northward"]):
                return np.random.uniform(-20, 20, shape)
            else:
                return np.random.uniform(0, 30, shape)

        # Humidity variables
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["humidity", "moisture", "rh"]
        ):
            if "relative" in standard_name or "relative" in long_name:
                # Relative humidity (0-100%)
                return np.random.uniform(20, 100, shape)
            else:
                # Specific humidity (small positive values)
                return np.random.uniform(0, 0.02, shape)

        # Radiation variables
        if any(
            x in standard_name or x in name.lower() or x in long_name for x in ["radiation", "flux"]
        ):
            # Radiation (positive values, 0-1000 W/m²)
            return np.random.uniform(0, 1000, shape)

        # Default: standard normal distribution
        return np.random.randn(*shape)

    # ------------------------------------------------------------
    # Build xarray.Dataset
    # ------------------------------------------------------------

    def to_xarray(self, validate=True):
        """
        Convert to a real xarray.Dataset.

        Parameters
        ----------
        validate : bool, default True
            Whether to validate the dataset before conversion

        Returns
        -------
        xarray.Dataset
            The constructed xarray Dataset

        Raises
        ------
        ValueError
            If validation fails or if any variable/coordinate is missing data
        """
        import xarray as xr

        if validate:
            self.validate(strict_coords=False)

        coords = {}
        for name, arr in self.coords.items():
            if arr.data is None:
                raise ValueError(f"Coordinate '{name}' missing data.")
            coords[name] = (arr.dims, arr.data, arr.attrs)

        variables = {}
        for name, arr in self.variables.items():
            if arr.data is None:
                raise ValueError(f"Variable '{name}' missing data.")
            variables[name] = (arr.dims, arr.data, arr.attrs)

        ds = xr.Dataset(data_vars=variables, coords=coords, attrs=self.attrs)

        # Apply encodings
        for name, arr in self.variables.items():
            if arr.encoding:
                ds[name].encoding = arr.encoding

        for name, arr in self.coords.items():
            if arr.encoding:
                ds[name].encoding = arr.encoding

        return ds

    # ------------------------------------------------------------
    # Zarr Builder
    # ------------------------------------------------------------

    def to_zarr(self, store_path, mode="w", validate=True):
        """
        Write dataset to Zarr format.

        Parameters
        ----------
        store_path : str
            Path to Zarr store
        mode : str, default "w"
            Write mode ('w' for write, 'a' for append)
        validate : bool, default True
            Whether to validate before writing

        Returns
        -------
        zarr.hierarchy.Group
            The Zarr group
        """
        ds = self.to_xarray(validate=validate)
        return ds.to_zarr(store_path, mode=mode)
