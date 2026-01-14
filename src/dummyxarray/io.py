"""
I/O operations for DummyDataset.

This module provides mixins for serialization, deserialization, and
conversion to/from xarray, Zarr, and STAC formats.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import DummyDataset

# Type variable for DummyDataset to handle forward references
D = TypeVar("D", bound="DummyDataset")

import yaml


class IOMixin:
    """Mixin providing I/O capabilities."""

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
        # Set default indent if not provided
        if "indent" not in kwargs:
            kwargs["indent"] = 2
        return json.dumps(self.to_dict(), **kwargs)

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
        # Import here to avoid circular dependency
        from .core import DummyArray

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
        # Import here to avoid circular dependency
        from .core import DummyArray

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

    def to_intake_catalog(
        self,
        name="dataset",
        description="Dataset generated by dummyxarray",
        driver="zarr",
        data_path=None,
        **kwargs,
    ):
        """
        Convert dataset to Intake catalog format.

        Parameters
        ----------
        name : str, default "dataset"
            Name for the data source in the catalog
        description : str, default "Dataset generated by dummyxarray"
            Description of the data source
        driver : str, default "zarr"
            Intake driver to use (zarr, netcdf, xarray, etc.)
        data_path : str, optional
            Path to the actual data file. If None, uses template path
        **kwargs
            Additional arguments to pass to the driver

        Returns
        -------
        str
            YAML string representing the Intake catalog

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 12)
        >>> ds.add_variable("temperature", dims=["time"], attrs={"units": "K"})
        >>> catalog_yaml = ds.to_intake_catalog(
        ...     name="my_dataset",
        ...     description="Temperature data",
        ...     data_path="data/my_dataset.zarr"
        ... )
        """
        # Build catalog structure
        catalog = {
            "metadata": {
                "version": 1,
                "description": f"Intake catalog for {name}",
            }
        }

        # Add dataset-level parameters if any
        if hasattr(self, "attrs") and self.attrs:
            catalog["metadata"]["dataset_attrs"] = dict(self.attrs)

        # Build sources section
        sources = {}

        # Default data path template if not provided
        if data_path is None:
            data_path = "{{ CATALOG_DIR }}/" + name + ".zarr"

        source_entry = {
            "description": description,
            "driver": driver,
            "args": {"urlpath": data_path, **kwargs},
        }

        # Add metadata about the dataset structure
        source_metadata = {}

        # Add dimension information
        if hasattr(self, "dims") and self.dims:
            source_metadata["dimensions"] = dict(self.dims)

        # Add coordinate information
        if hasattr(self, "coords") and self.coords:
            coord_info = {}
            for coord_name, coord_arr in self.coords.items():
                coord_info[coord_name] = {
                    "dims": coord_arr.dims,
                    "attrs": dict(coord_arr.attrs) if coord_arr.attrs else {},
                }
                if coord_arr.encoding:
                    encoding = dict(coord_arr.encoding)
                    # Convert tuples to lists for YAML compatibility
                    for key, value in encoding.items():
                        if isinstance(value, tuple):
                            encoding[key] = list(value)
                    coord_info[coord_name]["encoding"] = encoding
            source_metadata["coordinates"] = coord_info

        # Add variable information
        if hasattr(self, "variables") and self.variables:
            var_info = {}
            for var_name, var_arr in self.variables.items():
                var_info[var_name] = {
                    "dims": var_arr.dims,
                    "attrs": dict(var_arr.attrs) if var_arr.attrs else {},
                }
                if var_arr.encoding:
                    encoding = dict(var_arr.encoding)
                    # Convert tuples to lists for YAML compatibility
                    for key, value in encoding.items():
                        if isinstance(value, tuple):
                            encoding[key] = list(value)
                    var_info[var_name]["encoding"] = encoding
            source_metadata["variables"] = var_info

        if source_metadata:
            source_entry["metadata"] = source_metadata

        sources[name] = source_entry
        catalog["sources"] = sources

        return yaml.dump(catalog, sort_keys=False)

    def save_intake_catalog(
        self,
        path,
        name="dataset",
        description="Dataset generated by dummyxarray",
        driver="zarr",
        data_path=None,
        **kwargs,
    ):
        """
        Save Intake catalog to a YAML file.

        Parameters
        ----------
        path : str
            Output file path for the catalog YAML
        name : str, default "dataset"
            Name for the data source in the catalog
        description : str, default "Dataset generated by dummyxarray"
            Description of the data source
        driver : str, default "zarr"
            Intake driver to use (zarr, netcdf, xarray, etc.)
        data_path : str, optional
            Path to the actual data file. If None, uses template path
        **kwargs
            Additional arguments to pass to the driver
        """
        catalog_yaml = self.to_intake_catalog(
            name=name, description=description, driver=driver, data_path=data_path, **kwargs
        )

        with open(path, "w") as f:
            f.write(catalog_yaml)

    @classmethod
    def from_intake_catalog(cls, catalog_source, source_name=None):
        """
        Create a DummyDataset from an Intake catalog.

        Parameters
        ----------
        catalog_source : str or dict
            Either a path to a YAML catalog file or a dictionary containing
            the catalog structure
        source_name : str, optional
            Name of the source to use from the catalog. If None and catalog
            contains only one source, that source will be used automatically.

        Returns
        -------
        DummyDataset
            A new DummyDataset with the structure from the catalog

        Raises
        ------
        ValueError
            If catalog format is invalid or source_name is not found
        FileNotFoundError
            If catalog_source is a file path that doesn't exist

        Examples
        --------
        >>> # Load from file
        >>> ds = DummyDataset.from_intake_catalog("catalog.yaml", "climate_data")

        >>> # Load from dictionary
        >>> catalog_dict = yaml.safe_load(catalog_yaml)
        >>> ds = DummyDataset.from_intake_catalog(catalog_dict, "climate_data")
        """
        from pathlib import Path

        import yaml

        # Load catalog
        if isinstance(catalog_source, (str, Path)):
            # Load from file
            try:
                with open(catalog_source) as f:
                    catalog = yaml.safe_load(f)
            except FileNotFoundError as err:
                raise FileNotFoundError(f"Catalog file not found: {catalog_source}") from err
        elif isinstance(catalog_source, dict):
            # Use provided dictionary
            catalog = catalog_source
        else:
            raise ValueError("catalog_source must be a file path or dictionary")

        # Validate catalog structure
        if not isinstance(catalog, dict):
            raise ValueError("Catalog must be a dictionary")

        if "sources" not in catalog:
            raise ValueError("Catalog must contain 'sources' section")

        sources = catalog["sources"]
        if not sources:
            raise ValueError("Catalog sources section cannot be empty")

        # Determine which source to use
        if source_name is None:
            if len(sources) == 1:
                source_name = list(sources.keys())[0]
            else:
                raise ValueError(
                    "Multiple sources found in catalog. " "Please specify source_name explicitly."
                )

        if source_name not in sources:
            available_sources = list(sources.keys())
            raise ValueError(
                f"Source '{source_name}' not found in catalog. "
                f"Available sources: {available_sources}"
            )

        source = sources[source_name]

        # Create new DummyDataset
        ds = cls()

        # Extract dataset attributes from catalog metadata if available
        if "metadata" in catalog:
            catalog_metadata = catalog["metadata"]
            if "dataset_attrs" in catalog_metadata:
                ds.attrs.update(catalog_metadata["dataset_attrs"])

        # Extract source metadata if available
        source_metadata = source.get("metadata", {})

        # Add dimensions
        if "dimensions" in source_metadata:
            for dim_name, dim_size in source_metadata["dimensions"].items():
                ds.add_dim(dim_name, dim_size)

        # Add coordinates
        if "coordinates" in source_metadata:
            for coord_name, coord_info in source_metadata["coordinates"].items():
                coord_attrs = coord_info.get("attrs", {})
                coord_encoding = coord_info.get("encoding", {})
                ds.add_coord(
                    coord_name, dims=coord_info["dims"], attrs=coord_attrs, encoding=coord_encoding
                )

        # Add variables
        if "variables" in source_metadata:
            for var_name, var_info in source_metadata["variables"].items():
                var_attrs = var_info.get("attrs", {})
                var_encoding = var_info.get("encoding", {})
                ds.add_variable(
                    var_name, dims=var_info["dims"], attrs=var_attrs, encoding=var_encoding
                )

        # Add catalog-specific attributes
        ds.attrs.update(
            {
                "intake_catalog_source": source_name,
                "intake_driver": source.get("driver", "unknown"),
                "intake_description": source.get("description", ""),
            }
        )

        return ds

    @classmethod
    def load_intake_catalog(cls, path, source_name=None):
        """
        Load a DummyDataset from an Intake catalog YAML file.

        This is a convenience method that wraps from_intake_catalog() for file loading.

        Parameters
        ----------
        path : str
            Path to the catalog YAML file
        source_name : str, optional
            Name of the source to use from the catalog

        Returns
        -------
        DummyDataset
            A new DummyDataset with the structure from the catalog
        """
        return cls.from_intake_catalog(path, source_name)

    def to_stac_item(self, id, geometry=None, properties=None, assets=None, **kwargs):
        """
        Convert the dataset to a STAC Item.

        Requires the 'stac' optional dependency.

        Parameters
        ----------
        id : str
            Unique identifier for the STAC Item
        geometry : dict, optional
            GeoJSON geometry dictionary
        properties : dict, optional
            Additional properties for the STAC Item
        assets : dict, optional
            Dictionary of pystac.Asset objects
        **kwargs
            Additional arguments passed to pystac.Item

        Returns
        -------
        pystac.Item
            The generated STAC Item
        """
        try:
            from pystac import Item, Asset
            from .stac import dataset_to_stac_item
        except ImportError as e:
            raise ImportError(
                "STAC support requires 'pystac' and other optional dependencies. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        return dataset_to_stac_item(
            self, id=id, geometry=geometry, properties=properties, assets=assets, **kwargs
        )

    def to_stac_collection(
        self,
        id: str,
        description: Optional[str] = None,
        extent: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> "pystac.Collection":
        """
        Create a STAC Collection from this dataset.

        Parameters
        ----------
        id : str
            Unique identifier for the collection
        description : str, optional
            Detailed description of the collection
        extent : dict, optional
            Spatial and temporal extent of the collection. If not provided,
            will attempt to extract from dataset attributes.
        **kwargs
            Additional arguments passed to pystac.Collection

        Returns
        -------
        pystac.Collection
            The generated STAC Collection

        Examples
        --------
        >>> ds = DummyDataset()
        >>> collection = ds.to_stac_collection(
        ...     id="my-collection",
        ...     description="A collection of dummy data"
        ... )
        """
        try:
            from pystac import Collection
        except ImportError as e:
            raise ImportError(
                "STAC support requires 'pystac' and other optional "
                "dependencies. Install with: pip install 'dummyxarray[stac]'"
            ) from e

        # Create a default extent if not provided
        if extent is None:
            extent = self._get_default_stac_extent()

        # Create the collection
        collection = Collection(
            id=id,
            description=description or self.attrs.get("description", ""),
            extent=extent,
            **kwargs,
        )

        # Add dataset metadata
        self._add_collection_metadata(collection)

        return collection

    def _get_default_stac_extent(self) -> Dict[str, Any]:
        """Generate a default STAC extent from dataset attributes."""
        from pystac import SpatialExtent, TemporalExtent
        from dateutil.parser import parse

        extent = {"spatial": None, "temporal": None}

        # Try to get spatial extent
        if (
            hasattr(self, "attrs")
            and isinstance(self.attrs, dict)
            and "geospatial_bounds" in self.attrs
        ):
            coords = self.attrs["geospatial_bounds"]["coordinates"][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            bbox = [min(lons), min(lats), max(lons), max(lats)]
            extent["spatial"] = SpatialExtent(bboxes=[bbox])

        # Try to get temporal extent
        time_start = None
        time_end = None
        if hasattr(self, "attrs") and isinstance(self.attrs, dict):
            time_start = self.attrs.get("time_coverage_start")
            time_end = self.attrs.get("time_coverage_end", time_start)

        def _parse_dt(val):
            if val is None:
                return None
            if isinstance(val, str):
                try:
                    return parse(val)
                except (ValueError, TypeError):
                    return None
            return val

        start_dt = _parse_dt(time_start)
        end_dt = _parse_dt(time_end)
        if start_dt is not None or end_dt is not None:
            extent["temporal"] = TemporalExtent(intervals=[[start_dt, end_dt]])

        return extent

    def _add_collection_metadata(self, collection: "pystac.Collection") -> None:
        """Add dataset metadata to a STAC Collection."""
        if hasattr(self, "dims"):
            collection.extra_fields["dims"] = dict(self.dims)
        if hasattr(self, "variables"):
            collection.extra_fields["variables"] = list(self.variables.keys())

    @classmethod
    def from_stac_item(cls, item):
        """
        Create a DummyDataset from a STAC Item.

        Parameters
        ----------
        item : pystac.Item
            The STAC Item to convert

        Returns
        -------
        DummyDataset
            A new DummyDataset with the structure from the STAC Item
        """
        try:
            from .stac import stac_item_to_dataset
        except ImportError as e:
            raise ImportError(
                "STAC support requires 'pystac' and other optional dependencies. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        return stac_item_to_dataset(item)

    def save_stac_item(
        self: "D",
        path: str,
        id: Optional[str] = None,
        geometry: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        assets: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Save the dataset as a STAC Item to a file.

        Parameters
        ----------
        path : str
            Path where to save the STAC Item JSON file
        id : str, optional
            Unique identifier for the STAC Item. If not provided, will use the dataset name or a UUID.
        geometry : dict, optional
            GeoJSON geometry dict (required if not in dataset.attrs)
        properties : dict, optional
            Additional properties for the STAC Item
        assets : dict, optional
            Dictionary of asset information
        **kwargs
            Additional arguments passed to to_stac_item()
        """
        try:
            from pystac import Item
        except ImportError as e:
            raise ImportError(
                "STAC file operations require 'pystac'. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Convert to STAC Item
        item = self.to_stac_item(
            id=id or f"item-{str(uuid.uuid4())}",
            geometry=geometry,
            properties=properties,
            assets=assets,
            **kwargs,
        )

        # Save to file
        item.save_object(dest_href=path)

    def save_stac_collection(
        self: "D", path: str, id: Optional[str] = None, description: Optional[str] = None, **kwargs
    ) -> None:
        """
        Save the dataset as a STAC Collection to a file.

        Parameters
        ----------
        path : str
            Path where to save the STAC Collection JSON file
        id : str, optional
            Unique identifier for the STAC Collection
        description : str, optional
            Description of the collection
        **kwargs
            Additional arguments passed to to_stac_collection()
        """
        try:
            from pystac import Collection
        except ImportError as e:
            raise ImportError(
                "STAC file operations require 'pystac'. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Convert to STAC Collection
        collection = self.to_stac_collection(
            id=id or f"collection-{str(uuid.uuid4())}",
            description=description or "A collection of STAC items",
            **kwargs,
        )

        # Save to file
        collection.save_object(dest_href=path)

    @classmethod
    def load_stac_item(cls: type[D], path: str, **kwargs) -> D:
        """
        Load a STAC Item from a file and convert it to a DummyDataset.

        Parameters
        ----------
        path : str
            Path to the STAC Item JSON file
        **kwargs
            Additional arguments passed to from_stac_item()

        Returns
        -------
        DummyDataset
            The loaded dataset
        """
        try:
            from pystac import Item
        except ImportError as e:
            raise ImportError(
                "STAC file operations require 'pystac'. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        item = Item.from_file(path)
        return cls.from_stac_item(item, **kwargs)

    @classmethod
    def load_stac_collection(
        cls: type[D], path: str, item_loader: Optional[Callable[[Any], D]] = None, **kwargs
    ) -> Union[D, List[D]]:
        """
        Load a STAC Collection from a file and convert it to one or more DummyDatasets.

        Parameters
        ----------
        path : str
            Path to the STAC Collection JSON file
        item_loader : callable, optional
            Function to handle loading of individual items in the collection.
            If not provided, returns a list of DummyDatasets.
        **kwargs
            Additional arguments passed to from_stac_item()

        Returns
        -------
        DummyDataset or list of DummyDataset
            The loaded dataset(s)
        """
        try:
            from pystac import Collection
        except ImportError as e:
            raise ImportError(
                "STAC file operations require 'pystac'. "
                "Install with: pip install 'dummyxarray[stac]'"
            ) from e

        collection = Collection.from_file(path)

        if item_loader is not None:
            return item_loader(collection)

        # If no item_loader provided, attempt to convert the collection.
        # This will return:
        # - a DummyDataset (if no resolvable items)
        # - or a list of DummyDatasets (if items are available)
        return cls.from_stac_collection(collection, **kwargs)
