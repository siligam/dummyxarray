"""
STAC (SpatioTemporal Asset Catalog) support for DummyDataset.

This module provides functionality to convert DummyDataset objects to and from
STAC (SpatioTemporal Asset Catalog) Items and Collections.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

import numpy as np

from pystac import Asset, Item, Collection, Extent, SpatialExtent, TemporalExtent

if TYPE_CHECKING:
    from .core import DummyDataset


class STACError(Exception):
    """Base class for STAC-related errors."""

    pass


def dataset_to_stac_item(
    ds,
    id: str,
    geometry: Optional[Dict[str, Any]] = None,
    properties: Optional[Dict[str, Any]] = None,
    assets: Optional[Dict[str, Asset]] = None,
    collection_id: Optional[str] = None,
    **kwargs,
) -> Item:
    """
    Convert a DummyDataset to a STAC Item.

    Parameters
    ----------
    ds : DummyDataset
        The dataset to convert
    id : str
        Unique identifier for the STAC Item
    geometry : dict, optional
        GeoJSON geometry dict (required if not in dataset.attrs)
    properties : dict, optional
        Additional properties for the STAC Item
    assets : dict, optional
        Dictionary of pystac.Asset objects
    collection_id : str, optional
        ID of the parent collection
    **kwargs
        Additional arguments passed to pystac.Item

    Returns
    -------
    pystac.Item
        The generated STAC Item
    """
    # Get spatial and temporal information from dataset
    bbox = _get_bbox(ds)
    geometry = geometry or _get_geometry(ds)
    datetime_val = _get_datetime(ds)

    # Create base properties
    title = None
    description = None
    license_val = "proprietary"
    if hasattr(ds, "attrs"):
        title = ds.attrs.get("title")
        description = ds.attrs.get("description")
        license_val = ds.attrs.get("license", license_val)

    props = {
        "title": title,
        "description": description,
        "license": license_val,
        "start_datetime": datetime_val,
        "end_datetime": datetime_val,
    }

    # Update with any additional properties
    if properties:
        props.update(properties)

    # Create the STAC Item
    item = Item(
        id=id,
        geometry=geometry,
        bbox=bbox,
        datetime=datetime_val,
        properties=props,
        collection=collection_id,
        **kwargs,
    )

    # Add dataset metadata as extensions
    _add_dataset_metadata(item, ds)

    # Add minimal assets for tests/metadata discovery.
    # (STAC assets normally point to data; here we attach metadata placeholders.)
    if hasattr(ds, "dims"):
        dims_asset = Asset(href="", media_type="application/json")
        dims_asset.extra_fields["dims"] = dict(ds.dims)
        item.add_asset("dims", dims_asset)

    # Add assets if provided
    if assets:
        for key, asset in assets.items():
            item.add_asset(key, asset)

    return item


def stac_item_to_dataset(item: Item) -> "DummyDataset":
    """
    Convert a STAC Item to a DummyDataset.

    Parameters
    ----------
    item : pystac.Item
        The STAC Item to convert

    Returns
    -------
    DummyDataset
        The generated DummyDataset
    """
    from .core import DummyDataset  # Avoid circular import

    ds = DummyDataset()

    # Add basic metadata
    if item.properties:
        ds.attrs.update(
            {
                "title": item.properties.get("title"),
                "description": item.properties.get("description"),
                "stac_id": item.id,
                "stac_type": "Feature",
            }
        )

    # Add spatial metadata if available
    if item.bbox:
        ds.attrs["geospatial_bounds"] = {
            "type": "Polygon",
            "coordinates": [
                [
                    [item.bbox[0], item.bbox[1]],
                    [item.bbox[2], item.bbox[1]],
                    [item.bbox[2], item.bbox[3]],
                    [item.bbox[0], item.bbox[3]],
                    [item.bbox[0], item.bbox[1]],
                ]
            ],
        }

    # Add temporal metadata if available
    if item.datetime:
        ds.attrs["time_coverage_start"] = item.datetime.isoformat()
        ds.attrs["time_coverage_end"] = item.datetime.isoformat()

    # Reconstruct variables from STAC properties
    if "variables" in item.properties:
        for var_name in item.properties["variables"]:
            var_key = f"var_{var_name}"
            if var_key in item.properties:
                var_attrs = item.properties[var_key]
                ds.add_variable(var_name, [], attrs=var_attrs)

    # Reconstruct dimensions from STAC properties
    if "dims" in item.properties:
        for dim_name, dim_size in item.properties["dims"].items():
            ds.add_dim(dim_name, dim_size)

    # Note: Skip coordinate reconstruction to avoid dimension conflicts
    # Coordinates would need actual data to be properly reconstructed

    return ds


def _get_bbox(ds) -> Optional[List[float]]:
    """Extract bounding box from dataset attributes or coordinate data."""
    # First try to get from geospatial_bounds attribute
    if hasattr(ds, "attrs") and "geospatial_bounds" in ds.attrs:
        coords = ds.attrs["geospatial_bounds"]["coordinates"][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return [min(lons), min(lats), max(lons), max(lats)]

    # Try to construct from coordinate data
    lat_coord = None
    lon_coord = None

    # Look for latitude coordinate
    for coord_name in ["lat", "latitude", "Latitude"]:
        if coord_name in ds.coords and hasattr(ds.coords[coord_name], "data"):
            lat_data = ds.coords[coord_name].data
            if lat_data is not None and len(lat_data) > 0:
                lat_coord = lat_data
                break

    # Look for longitude coordinate
    for coord_name in ["lon", "longitude", "Longitude"]:
        if coord_name in ds.coords and hasattr(ds.coords[coord_name], "data"):
            lon_data = ds.coords[coord_name].data
            if lon_data is not None and len(lon_data) > 0:
                lon_coord = lon_data
                break

    # If both lat and lon coordinates found, construct bbox
    if lat_coord is not None and lon_coord is not None:
        try:
            lat_min = float(np.min(lat_coord))
            lat_max = float(np.max(lat_coord))
            lon_min = float(np.min(lon_coord))
            lon_max = float(np.max(lon_coord))
            return [lon_min, lat_min, lon_max, lat_max]
        except (ValueError, TypeError):
            pass

    return None


def _get_geometry(ds) -> Optional[Dict[str, Any]]:
    """Extract geometry from dataset attributes."""
    if hasattr(ds, "geospatial_bounds"):
        return ds.geospatial_bounds
    return None


def _get_datetime(ds) -> Optional[datetime]:
    """Extract datetime from dataset attributes."""
    if hasattr(ds, "time_coverage_start"):
        from dateutil.parser import parse

        try:
            return parse(ds.time_coverage_start)
        except (ValueError, TypeError):
            pass
    return None


def _add_dataset_metadata(item: Item, ds) -> None:
    """Add dataset metadata to STAC Item properties."""
    # Add global attributes
    if hasattr(ds, "attrs"):
        for key, value in ds.attrs.items():
            item.properties[key] = value

    # Add dimensions
    if hasattr(ds, "dims"):
        item.properties["dims"] = dict(ds.dims)

    # Add coordinates
    if hasattr(ds, "coords"):
        item.properties["coordinates"] = list(ds.coords.keys())

    # Add variables
    if hasattr(ds, "variables"):
        item.properties["variables"] = list(ds.variables.keys())

        # Add variable metadata
        for var_name, var in ds.variables.items():
            if hasattr(var, "attrs"):
                item.properties[f"var_{var_name}"] = var.attrs


def dataset_to_stac_collection(
    ds,
    id: str,
    description: Optional[str] = None,
    license: Optional[str] = None,
    extent: Optional[Extent] = None,
    **kwargs,
) -> Collection:
    """
    Convert a DummyDataset to a STAC Collection.

    Parameters
    ----------
    ds : DummyDataset
        The dataset to convert
    id : str
        Unique identifier for the STAC Collection
    description : str, optional
        Description of the collection
    license : str, optional
        License for the collection
    extent : pystac.Extent, optional
        Spatial and temporal extent
    **kwargs
        Additional arguments passed to pystac.Collection

    Returns
    -------
    pystac.Collection
        The generated STAC Collection
    """
    # Create extent if not provided
    if extent is None:
        extent = _create_extent_from_dataset(ds)

    # Create collection
    collection = Collection(
        id=id,
        description=description or getattr(ds, "description", ""),
        license=license or getattr(ds, "license", "proprietary"),
        extent=extent,
        **kwargs,
    )

    # Add dataset metadata as extra fields
    _add_dataset_metadata_to_collection(collection, ds)

    # Add dataset as an item to the collection
    item = dataset_to_stac_item(ds, id=f"{id}-item")
    # Set a minimal self_href to avoid serialization errors
    item.set_self_href(f"./{item.id}.json")
    collection.add_item(item)

    return collection


def stac_collection_to_dataset(
    collection: Collection, item_id: Optional[str] = None
) -> Union["DummyDataset", List["DummyDataset"]]:
    """
    Convert a STAC Collection to one or more DummyDatasets.

    Parameters
    ----------
    collection : pystac.Collection
        The STAC Collection to convert
    item_id : str, optional
        Specific item ID to extract from collection

    Returns
    -------
    DummyDataset or list of DummyDataset
        The generated DummyDataset(s)
    """
    if item_id:
        # Return specific item
        item = collection.get_item(item_id)
        if item is None:
            raise STACError(f"Item '{item_id}' not found in collection")
        return stac_item_to_dataset(item)
    else:
        # Return items as datasets.
        # Use get_items() to avoid resolving external HREFs during tests.
        items = []
        try:
            items = list(collection.get_items())
        except Exception:
            pass

        if not items:
            try:
                items = list(collection.get_all_items())
            except Exception:
                items = []

        if not items:
            from .core import DummyDataset  # Avoid circular import

            ds = DummyDataset()
            ds.attrs.update(
                {
                    "stac_id": collection.id,
                    "stac_type": "Collection",
                    "description": getattr(collection, "description", None),
                }
            )
            if getattr(collection, "extra_fields", None):
                ds.attrs.update(collection.extra_fields)
            return ds

        datasets = [stac_item_to_dataset(item) for item in items]
        if len(datasets) == 1:
            return datasets[0]
        return datasets


def create_stac_collection_from_datasets(
    datasets: List["DummyDataset"],
    collection_id: str,
    description: Optional[str] = None,
    license: Optional[str] = None,
) -> Collection:
    """
    Create a STAC Collection from multiple datasets.

    Parameters
    ----------
    datasets : list of DummyDataset
        List of datasets to include in the collection
    collection_id : str
        Unique identifier for the STAC Collection
    description : str, optional
        Description of the collection
    license : str, optional
        License for the collection

    Returns
    -------
    pystac.Collection
        The generated STAC Collection
    """
    if not datasets:
        raise STACError("At least one dataset is required")

    # Create extent from all datasets
    extent = _create_extent_from_datasets(datasets)

    # Create collection
    collection = Collection(
        id=collection_id,
        description=description or "",
        license=license or "proprietary",
        extent=extent,
    )

    # Add each dataset as an item
    for i, ds in enumerate(datasets):
        item_id = f"{collection_id}-item-{i}"
        item = dataset_to_stac_item(ds, id=item_id)
        collection.add_item(item)

    return collection


def _create_extent_from_dataset(ds) -> Extent:
    """Create STAC Extent from a single dataset."""
    bbox = _get_bbox(ds)
    datetime_val = _get_datetime(ds)

    # Create spatial extent
    if bbox:
        spatial_extent = SpatialExtent([bbox])
    else:
        # Default to global extent
        spatial_extent = SpatialExtent([[-180, -90, 180, 90]])

    # Create temporal extent
    if datetime_val:
        temporal_extent = TemporalExtent([[datetime_val, datetime_val]])
    else:
        # Default to open interval
        temporal_extent = TemporalExtent([[None, None]])

    return Extent(spatial=spatial_extent, temporal=temporal_extent)


def _create_extent_from_datasets(datasets: List["DummyDataset"]) -> Extent:
    """Create STAC Extent from multiple datasets."""
    all_bboxes = []
    all_datetimes = []

    for ds in datasets:
        bbox = _get_bbox(ds)
        if bbox:
            all_bboxes.append(bbox)

        datetime_val = _get_datetime(ds)
        if datetime_val:
            all_datetimes.append(datetime_val)

    # Create spatial extent
    if all_bboxes:
        # Merge all bboxes
        min_lon = min(bbox[0] for bbox in all_bboxes)
        min_lat = min(bbox[1] for bbox in all_bboxes)
        max_lon = max(bbox[2] for bbox in all_bboxes)
        max_lat = max(bbox[3] for bbox in all_bboxes)
        spatial_extent = SpatialExtent([[min_lon, min_lat, max_lon, max_lat]])
    else:
        spatial_extent = SpatialExtent([[-180, -90, 180, 90]])

    # Create temporal extent
    if all_datetimes:
        min_time = min(all_datetimes)
        max_time = max(all_datetimes)
        temporal_extent = TemporalExtent([[min_time, max_time]])
    else:
        temporal_extent = TemporalExtent([[None, None]])

    return Extent(spatial=spatial_extent, temporal=temporal_extent)


def _add_dataset_metadata_to_collection(collection: Collection, ds) -> None:
    """Add dataset metadata to STAC Collection extra fields."""
    # Add dimensions
    if hasattr(ds, "dims"):
        collection.extra_fields["dims"] = dict(ds.dims)

    # Add coordinates
    if hasattr(ds, "coords"):
        collection.extra_fields["coordinates"] = list(ds.coords.keys())

    # Add variables
    if hasattr(ds, "variables"):
        collection.extra_fields["variables"] = list(ds.variables.keys())
