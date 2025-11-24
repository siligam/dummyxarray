"""
History tracking and visualization for DummyDataset.

This module provides mixins for recording, replaying, and visualizing
operation history.
"""

import json

import yaml


class HistoryMixin:
    """Mixin providing history tracking and visualization capabilities."""

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
