"""Multi-file dataset support for DummyDataset.

This module provides functionality to open and combine multiple NetCDF files
into a single DummyDataset, tracking which files contribute to which coordinate ranges.
"""

import glob
from typing import TYPE_CHECKING, Any, Dict, List, Union

import xarray as xr

if TYPE_CHECKING:
    from .core import DummyDataset


def open_mfdataset(
    paths: Union[str, List[str]],
    concat_dim: str = "time",
    combine: str = "nested",
    **kwargs: Any,
) -> "DummyDataset":
    """Open multiple files as a single DummyDataset with file tracking.

    This function reads metadata from multiple NetCDF files and combines them
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
    >>> from dummyxarray import DummyDataset
    >>> ds = DummyDataset.open_mfdataset("data/*.nc", concat_dim="time")
    >>> files = ds.get_source_files(time=slice(0, 10))
    >>> print(files)
    ['data/file1.nc', 'data/file2.nc']

    Notes
    -----
    - Only metadata is loaded; no actual data arrays are read
    - Files must have compatible structures (same variables, compatible coordinates)
    - The concat_dim must exist in all files
    """
    # Expand glob pattern if needed
    if isinstance(paths, str):
        file_paths = sorted(glob.glob(paths))
        if not file_paths:
            raise ValueError(f"No files found matching pattern: {paths}")
    else:
        file_paths = list(paths)

    if not file_paths:
        raise ValueError("No files provided")

    # Read metadata from all files
    file_metadata = []
    for filepath in file_paths:
        metadata = _read_file_metadata(filepath, concat_dim)
        metadata["filepath"] = filepath
        file_metadata.append(metadata)

    # Validate compatibility
    _validate_file_compatibility(file_metadata, concat_dim)

    # Create combined DummyDataset
    combined_ds = _combine_file_metadata(file_metadata, concat_dim)

    # Enable file tracking and register sources
    combined_ds.enable_file_tracking(concat_dim=concat_dim)

    # Add file sources with coordinate ranges
    for metadata in file_metadata:
        coord_range = metadata["coord_ranges"][concat_dim]
        combined_ds.add_file_source(
            filepath=metadata["filepath"],
            coord_range=coord_range,
            metadata={
                "dims": metadata["dims"],
                "variables": list(metadata["variables"].keys()),
                "attrs": metadata["attrs"],
            },
        )

    return combined_ds


def _read_file_metadata(filepath: str, concat_dim: str) -> Dict[str, Any]:
    """Read metadata from a single file.

    Parameters
    ----------
    filepath : str
        Path to the NetCDF file
    concat_dim : str
        The concatenation dimension

    Returns
    -------
    dict
        Dictionary containing file metadata
    """
    # Open file to read metadata only
    with xr.open_dataset(filepath) as ds:
        metadata = {
            "dims": dict(ds.dims),
            "coords": {},
            "variables": {},
            "attrs": dict(ds.attrs),
            "coord_ranges": {},
        }

        # Extract coordinate metadata
        for coord_name, coord in ds.coords.items():
            metadata["coords"][coord_name] = {
                "dims": coord.dims,
                "attrs": dict(coord.attrs),
                "dtype": str(coord.dtype),
                "shape": coord.shape,
            }

            # Store coordinate range for concat_dim
            if coord_name == concat_dim:
                coord_values = coord.values
                metadata["coord_ranges"][concat_dim] = (
                    coord_values[0],
                    coord_values[-1],
                )

        # Extract variable metadata
        for var_name, var in ds.data_vars.items():
            metadata["variables"][var_name] = {
                "dims": var.dims,
                "attrs": dict(var.attrs),
                "dtype": str(var.dtype),
                "shape": var.shape,
            }

    return metadata


def _validate_file_compatibility(file_metadata: List[Dict[str, Any]], concat_dim: str) -> None:
    """Validate that files are compatible for concatenation.

    Parameters
    ----------
    file_metadata : list of dict
        List of metadata dictionaries from each file
    concat_dim : str
        The concatenation dimension

    Raises
    ------
    ValueError
        If files are incompatible
    """
    if not file_metadata:
        return

    first = file_metadata[0]

    # Check that concat_dim exists in all files
    for i, metadata in enumerate(file_metadata):
        if concat_dim not in metadata["dims"]:
            raise ValueError(
                f"Concatenation dimension '{concat_dim}' not found in file: "
                f"{metadata.get('filepath', f'file {i}')}"
            )

    # Check that all files have the same variables
    first_vars = set(first["variables"].keys())
    for i, metadata in enumerate(file_metadata[1:], start=1):
        vars_set = set(metadata["variables"].keys())
        if vars_set != first_vars:
            missing = first_vars - vars_set
            extra = vars_set - first_vars
            msg = f"Variable mismatch in file {i}:"
            if missing:
                msg += f" missing {missing}"
            if extra:
                msg += f" extra {extra}"
            raise ValueError(msg)

    # Check that variables have compatible dimensions
    for var_name in first_vars:
        first_dims = first["variables"][var_name]["dims"]
        for i, metadata in enumerate(file_metadata[1:], start=1):
            dims = metadata["variables"][var_name]["dims"]
            if dims != first_dims:
                raise ValueError(
                    f"Dimension mismatch for variable '{var_name}' in file {i}: "
                    f"expected {first_dims}, got {dims}"
                )


def _combine_file_metadata(file_metadata: List[Dict[str, Any]], concat_dim: str) -> "DummyDataset":
    """Combine metadata from multiple files into a single DummyDataset.

    Parameters
    ----------
    file_metadata : list of dict
        List of metadata dictionaries from each file
    concat_dim : str
        The concatenation dimension

    Returns
    -------
    DummyDataset
        Combined dataset with metadata from all files
    """
    from .core import DummyDataset

    # Start with first file's structure
    first = file_metadata[0]
    ds = DummyDataset()

    # Set global attributes (from first file)
    for key, value in first["attrs"].items():
        ds.assign_attrs(**{key: value})

    # Add dimensions (combine concat_dim sizes)
    total_concat_size = sum(m["dims"][concat_dim] for m in file_metadata)
    for dim_name, size in first["dims"].items():
        if dim_name == concat_dim:
            ds.add_dim(dim_name, total_concat_size)
        else:
            ds.add_dim(dim_name, size)

    # Add coordinates
    for coord_name, coord_info in first["coords"].items():
        ds.add_coord(
            coord_name,
            dims=list(coord_info["dims"]),
            attrs=coord_info["attrs"],
        )

    # Add variables
    for var_name, var_info in first["variables"].items():
        ds.add_variable(
            var_name,
            dims=list(var_info["dims"]),
            attrs=var_info["attrs"],
        )

    return ds
