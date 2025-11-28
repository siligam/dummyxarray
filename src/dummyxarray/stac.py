"""
STAC (SpatioTemporal Asset Catalog) support for DummyDataset.

This module provides functionality to convert DummyDataset objects to and from
STAC (SpatioTemporal Asset Catalog) Items and Collections.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pystac import Asset, Item

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
    **kwargs
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
    props = {
        "title": getattr(ds, "title", None),
        "description": getattr(ds, "description", None),
        "license": getattr(ds, "license", "proprietary"),
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
        **kwargs
    )
    
    # Add dataset metadata as extensions
    _add_dataset_metadata(item, ds)

    # Add assets if provided
    if assets:
        for key, asset in assets.items():
            item.add_asset(key, asset)
    
    return item

def stac_item_to_dataset(item: Item) -> 'DummyDataset':
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
                'title': item.properties.get('title'),
                'description': item.properties.get('description'),
                'stac_id': item.id,
                'stac_type': 'Feature',
            }
        )
    
    # Add spatial metadata if available
    if item.bbox:
        ds.attrs['geospatial_bounds'] = {
            'type': 'Polygon',
            'coordinates': [[
                [item.bbox[0], item.bbox[1]],
                [item.bbox[2], item.bbox[1]],
                [item.bbox[2], item.bbox[3]],
                [item.bbox[0], item.bbox[3]],
                [item.bbox[0], item.bbox[1]]
            ]]
        }
    
    # Add temporal metadata if available
    if item.datetime:
        ds.attrs['time_coverage_start'] = item.datetime.isoformat()
        ds.attrs['time_coverage_end'] = item.datetime.isoformat()

    return ds

def _get_bbox(ds) -> Optional[List[float]]:
    """Extract bounding box from dataset attributes."""
    if hasattr(ds, 'geospatial_bounds'):
        # Extract bbox from geospatial_bounds if available
        coords = ds.geospatial_bounds['coordinates'][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return [min(lons), min(lats), max(lons), max(lats)]
    return None

def _get_geometry(ds) -> Optional[Dict[str, Any]]:
    """Extract geometry from dataset attributes."""
    if hasattr(ds, 'geospatial_bounds'):
        return ds.geospatial_bounds
    return None

def _get_datetime(ds) -> Optional[datetime]:
    """Extract datetime from dataset attributes."""
    if hasattr(ds, 'time_coverage_start'):
        from dateutil.parser import parse
        try:
            return parse(ds.time_coverage_start)
        except (ValueError, TypeError):
            pass
    return None

def _add_dataset_metadata(item: Item, ds) -> None:
    """Add dataset metadata to STAC Item properties."""
    # Add dimensions
    if hasattr(ds, 'dims'):
        item.properties['dims'] = dict(ds.dims)

    # Add coordinates
    if hasattr(ds, 'coords'):
        item.properties['coordinates'] = list(ds.coords.keys())

    # Add variables
    if hasattr(ds, 'variables'):
        item.properties['variables'] = list(ds.variables.keys())

        # Add variable metadata
        for var_name, var in ds.variables.items():
            if hasattr(var, 'attrs'):
                item.properties[f'var_{var_name}'] = var.attrs
