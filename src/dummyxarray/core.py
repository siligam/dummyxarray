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
    
    def __init__(self, dims=None, attrs=None, data=None, encoding=None):
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
        """
        self.dims = dims
        self.attrs = attrs or {}
        self.data = data
        self.encoding = encoding or {}

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
    
    def __init__(self):
        """Initialize an empty DummyDataset."""
        self.dims = {}        # dim_name → size
        self.coords = {}      # coord_name → DummyArray
        self.variables = {}   # var_name  → DummyArray
        self.attrs = {}       # global attributes

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
        arr = DummyArray(dims, attrs, data, encoding)
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
        arr = DummyArray(dims, attrs, data, encoding)
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
