"""
Provenance tracking for DummyDataset.

This module provides mixins for tracking and visualizing state changes
(before/after) for each operation.
"""


class ProvenanceMixin:
    """Mixin providing provenance tracking capabilities."""

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
