"""
Dataset validation for DummyDataset.

This module provides mixins for validating dataset structure.
"""

import numpy as np


class ValidationMixin:
    """Mixin providing dataset validation capabilities."""

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
