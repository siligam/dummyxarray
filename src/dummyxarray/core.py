"""
Core classes for dummyxarray.

Provides DummyArray and DummyDataset classes with modular functionality
through mixins.
"""

import numpy as np

# Import mixins
from .cf_compliance import CFComplianceMixin
from .cf_standards import CFStandardsMixin
from .data_generation import DataGenerationMixin
from .history import HistoryMixin
from .io import IOMixin
from .mixins.file_tracker import FileTrackerMixin
from .provenance import ProvenanceMixin
from .validation import ValidationMixin


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
                init_args["data"] = "<data>"
            if encoding:
                init_args["encoding"] = encoding
            self._record_operation("__init__", init_args)

    def __repr__(self):
        """Return a string representation of the DummyArray."""
        lines = ["<dummyxarray.DummyArray>"]

        # Dimensions
        if self.dims:
            lines.append(f"Dimensions: ({', '.join(self.dims)})")
        else:
            lines.append("Dimensions: ()")

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
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
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
            List of operations

        Examples
        --------
        >>> arr = DummyArray(dims=["time"], attrs={"units": "days"})
        >>> arr.get_history()
        [{'func': '__init__', 'args': {'dims': ['time'], 'attrs': {'units': 'days'}}}]
        """
        return self._history.copy() if self._history is not None else []

    def replay_history(self, history=None):
        """
        Replay a sequence of operations to recreate an array.

        Parameters
        ----------
        history : list of dict, optional
            History to replay. If None, uses self.get_history()

        Returns
        -------
        DummyArray
            New array with operations replayed
        """
        if history is None:
            history = self.get_history()

        # Get __init__ args
        init_op = history[0] if history and history[0]["func"] == "__init__" else {}
        init_args = init_op.get("args", {})

        # Create new array
        arr = DummyArray(**init_args, _record_history=False)

        # Replay other operations
        for op in history[1:]:
            func = getattr(arr, op["func"], None)
            if func and callable(func):
                func(**op["args"])

        return arr

    def assign_attrs(self, **kwargs):
        """
        Assign new attributes to this array (xarray-compatible API).

        Parameters
        ----------
        **kwargs
            Attributes to assign

        Returns
        -------
        self
            Returns self for method chaining

        Examples
        --------
        >>> arr = DummyArray(dims=["time"])
        >>> arr.assign_attrs(units="days", calendar="gregorian")
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
            Dictionary representation
        """
        return {
            "dims": self.dims,
            "attrs": self.attrs,
            "encoding": self.encoding,
            "has_data": self.data is not None,
        }


class DummyDataset(
    HistoryMixin,
    ProvenanceMixin,
    CFComplianceMixin,
    CFStandardsMixin,
    IOMixin,
    ValidationMixin,
    DataGenerationMixin,
    FileTrackerMixin,
):
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
        # Allow private attributes (starting with _) for mixins
        if name in ("dims", "coords", "variables", "attrs", "_history") or name.startswith("_"):
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
    # Core API
    # ------------------------------------------------------------

    def set_global_attrs(self, **kwargs):
        """
        Set or update global dataset attributes.

        Parameters
        ----------
        **kwargs
            Attributes to set

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.set_global_attrs(title="My Dataset", institution="DKRZ")
        """
        self.attrs.update(kwargs)

    def assign_attrs(self, **kwargs):
        """
        Assign new global attributes to this dataset (xarray-compatible API).

        Parameters
        ----------
        **kwargs
            Attributes to assign

        Returns
        -------
        self
            Returns self for method chaining

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.assign_attrs(title="My Dataset", institution="DKRZ")
        """
        # Capture provenance
        provenance = {"modified": {}}
        for key, value in kwargs.items():
            old_value = self.attrs.get(key)
            provenance["modified"][key] = {"before": old_value, "after": value}

        self._record_operation("assign_attrs", kwargs, provenance)
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

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_dim("lat", 64)
        """
        # Capture provenance
        if name in self.dims:
            provenance = {"modified": {name: {"before": self.dims[name], "after": size}}}
        else:
            provenance = {"added": [name]}

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
            Dimension names
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
            Dimension names
        attrs : dict, optional
            Metadata attributes
        data : array-like, optional
            Variable data
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

    @classmethod
    def open_mfdataset(cls, paths, concat_dim="time", combine="nested", **kwargs):
        """Open multiple files as a single DummyDataset with file tracking.

        This class method reads metadata from multiple NetCDF files and combines them
        into a single DummyDataset, tracking which files contribute to which
        coordinate ranges along the concatenation dimension.

        Parameters
        ----------
        paths : str or list of str
            Either a glob pattern (e.g., "data/*.nc") or a list of file paths
        concat_dim : str, optional
            The dimension along which to concatenate files (default: "time")
        combine : str, optional
            How to combine datasets. Currently supports "nested" (default)
        **kwargs : optional
            Additional keyword arguments (reserved for future use)

        Returns
        -------
        DummyDataset
            A DummyDataset with metadata from all files and file tracking enabled

        Examples
        --------
        >>> ds = DummyDataset.open_mfdataset("data/*.nc", concat_dim="time")
        >>> files = ds.get_source_files(time=slice(0, 10))
        >>> print(files)
        ['data/file1.nc', 'data/file2.nc']

        See Also
        --------
        enable_file_tracking : Enable file tracking on an existing dataset
        get_source_files : Query which files contain specific coordinate ranges
        """
        from .mfdataset import open_mfdataset

        return open_mfdataset(paths, concat_dim=concat_dim, combine=combine, **kwargs)
