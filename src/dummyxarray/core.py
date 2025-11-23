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
import yaml
import numpy as np


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
                init_args['dims'] = dims
            if attrs:
                init_args['attrs'] = attrs
            if data is not None:
                init_args['data'] = '<data>'  # Don't store actual data
            if encoding:
                init_args['encoding'] = encoding
            self._record_operation('__init__', init_args)

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
            self._history.append({
                'func': func_name,
                'args': args
            })
    
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
        init_op = next((op for op in history if op['func'] == '__init__'), None)
        if init_op:
            arr = DummyArray(**init_op['args'], _record_history=False)
        else:
            arr = DummyArray(_record_history=False)
        
        # Replay other operations
        for op in history:
            if op['func'] == '__init__':
                continue
            
            func = getattr(arr, op['func'], None)
            if func and callable(func):
                func(**op['args'])
        
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
        self._record_operation('assign_attrs', kwargs)
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
        self.dims = {}        # dim_name → size
        self.coords = {}      # coord_name → DummyArray
        self.variables = {}   # var_name  → DummyArray
        self.attrs = {}       # global attributes
        
        # Operation history tracking
        self._history = [] if _record_history else None
        if _record_history:
            self._record_operation('__init__', {})

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
        if name in ('dims', 'coords', 'variables', 'attrs', '_history'):
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
            self._history.append({
                'func': func_name,
                'args': args
            })
    
    def get_history(self):
        """
        Get the operation history for this dataset.
        
        Returns
        -------
        list of dict
            List of operations, each with 'func' and 'args' keys
            
        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.assign_attrs(title="Test")
        >>> ds.get_history()
        [{'func': '__init__', 'args': {}},
         {'func': 'add_dim', 'args': {'name': 'time', 'size': 10}},
         {'func': 'assign_attrs', 'args': {'title': 'Test'}}]
        """
        return self._history.copy() if self._history is not None else []
    
    def export_history(self, format='json'):
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
        
        if format == 'json':
            return json.dumps(history, indent=2)
        elif format == 'yaml':
            return yaml.dump(history, default_flow_style=False)
        elif format == 'python':
            lines = []
            for op in history:
                if op['func'] == '__init__':
                    lines.append("ds = DummyDataset()")
                else:
                    args_str = ', '.join(f"{k}={repr(v)}" for k, v in op['args'].items())
                    lines.append(f"ds.{op['func']}({args_str})")
            return '\n'.join(lines)
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
            if op['func'] == '__init__':
                continue
            
            func = getattr(ds, op['func'], None)
            if func and callable(func):
                func(**op['args'])
        
        return ds

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
        self._record_operation('assign_attrs', kwargs)
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
        self._record_operation('add_dim', {'name': name, 'size': size})
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
        args = {'name': name}
        if dims is not None:
            args['dims'] = dims
        if attrs:
            args['attrs'] = attrs
        if data is not None:
            args['data'] = '<data>'
        if encoding:
            args['encoding'] = encoding
        self._record_operation('add_coord', args)
        
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
        args = {'name': name}
        if dims is not None:
            args['dims'] = dims
        if attrs:
            args['attrs'] = attrs
        if data is not None:
            args['data'] = '<data>'
        if encoding:
            args['encoding'] = encoding
        self._record_operation('add_variable', args)
        
        arr = DummyArray(dims, attrs, data, encoding, _record_history=False)
        self._infer_and_register_dims(arr)
        self.variables[name] = arr

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
                    errors.append(
                        f"{name}: Data shape {shape} does not match dims {dim_sizes}."
                    )

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
            "variables":   {k: v.to_dict() for k, v in self.variables.items()},
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
                dims=info["dims"],
                attrs=info["attrs"],
                data=None,
                encoding=info.get("encoding", {})
            )

        for name, info in spec.get("variables", {}).items():
            ds.variables[name] = DummyArray(
                dims=info["dims"],
                attrs=info["attrs"],
                data=None,
                encoding=info.get("encoding", {})
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
                encoding=dict(coord_var.encoding) if hasattr(coord_var, 'encoding') else {}
            )
        
        # Extract data variables
        for var_name, var in xr_dataset.data_vars.items():
            ds.variables[var_name] = DummyArray(
                dims=list(var.dims),
                attrs=dict(var.attrs),
                data=var.values if include_data else None,
                encoding=dict(var.encoding) if hasattr(var, 'encoding') else {}
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
                coord_array.data = self._generate_coordinate_data(
                    coord_name, coord_array
                )
        
        # Populate variables
        for var_name, var_array in self.variables.items():
            if var_array.data is None:
                var_array.data = self._generate_variable_data(
                    var_name, var_array
                )
        
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
        if any(x in standard_name or x in name.lower() or x in long_name 
               for x in ["temperature", "temp", "tas", "ts"]):
            if "k" == units or "kelvin" in units:
                # Temperature in Kelvin (250-310K range)
                return np.random.uniform(250, 310, shape)
            elif "c" == units or "celsius" in units or "degc" in units:
                # Temperature in Celsius (-30 to 40C range)
                return np.random.uniform(-30, 40, shape)
            else:
                return np.random.uniform(250, 310, shape)
        
        # Pressure variables (check before precipitation to avoid "pr" conflict)
        if any(x in standard_name or x in name.lower() or x in long_name
               for x in ["pressure", "pres", "psl"]):
            if "sea_level" in standard_name or "msl" in name.lower() or "psl" in name.lower():
                # Sea level pressure (980-1040 hPa)
                return np.random.uniform(98000, 104000, shape)
            else:
                # Generic pressure
                return np.random.uniform(50000, 105000, shape)
        
        # Precipitation variables
        if any(x in standard_name or x in name.lower() or x in long_name
               for x in ["precipitation", "precip", "rain"]) or name.lower() == "pr":
            # Precipitation (always positive, skewed distribution)
            return np.random.exponential(0.001, shape)
        
        # Wind variables
        if any(x in standard_name or x in name.lower() or x in long_name
               for x in ["wind", "velocity"]):
            # Wind speed (0-30 m/s, can be negative for components)
            if any(x in name.lower() for x in ["u", "zonal", "eastward"]):
                return np.random.uniform(-20, 20, shape)
            elif any(x in name.lower() for x in ["v", "meridional", "northward"]):
                return np.random.uniform(-20, 20, shape)
            else:
                return np.random.uniform(0, 30, shape)
        
        # Humidity variables
        if any(x in standard_name or x in name.lower() or x in long_name
               for x in ["humidity", "moisture", "rh"]):
            if "relative" in standard_name or "relative" in long_name:
                # Relative humidity (0-100%)
                return np.random.uniform(20, 100, shape)
            else:
                # Specific humidity (small positive values)
                return np.random.uniform(0, 0.02, shape)
        
        # Radiation variables
        if any(x in standard_name or x in name.lower() or x in long_name
               for x in ["radiation", "flux"]):
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
        
        ds = xr.Dataset(
            data_vars=variables,
            coords=coords,
            attrs=self.attrs
        )

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
