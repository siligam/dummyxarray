"""Multi-file dataset support for DummyDataset.

This module provides functionality to open and combine multiple NetCDF files
into a single DummyDataset, tracking which files contribute to which coordinate ranges.
"""

import glob
from typing import TYPE_CHECKING, Any, Dict, List, Union

import xarray as xr

from .time_utils import (
    add_frequency,
    count_timesteps,
    create_time_periods,
    infer_time_frequency,
)

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
    # Open file to read metadata only (don't decode times to preserve units)
    with xr.open_dataset(filepath, decode_times=False) as ds:
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

                # Infer frequency for time-like coordinates
                if "units" in coord.attrs and "since" in coord.attrs["units"]:
                    freq = infer_time_frequency(
                        coord_values, coord.attrs["units"], coord.attrs.get("calendar", "standard")
                    )
                    if freq:
                        metadata["coords"][coord_name]["attrs"]["frequency"] = freq

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


def groupby_time_impl(
    ds: "DummyDataset",
    freq: str,
    dim: str = "time",
    normalize_units: bool = True,
) -> List["DummyDataset"]:
    """Implementation of time-based grouping for DummyDataset.

    Parameters
    ----------
    ds : DummyDataset
        Dataset to group
    freq : str
        Grouping frequency (e.g., '10Y', '5Y', '1M')
    dim : str
        Time dimension to group by
    normalize_units : bool
        Update time units to reference each group's start

    Returns
    -------
    list of DummyDataset
        One dataset per time group
    """
    import cftime

    # Validate dimension exists
    if dim not in ds.dims:
        raise ValueError(f"Dimension '{dim}' not found in dataset")

    if dim not in ds.coords:
        raise ValueError(f"Coordinate '{dim}' not found in dataset")

    # Get time coordinate metadata
    time_coord = ds.coords[dim]

    if "units" not in time_coord.attrs:
        raise ValueError(f"Time coordinate '{dim}' has no units attribute")

    if "frequency" not in time_coord.attrs:
        raise ValueError(
            f"Time coordinate '{dim}' has no frequency attribute. "
            "Dataset must be opened with open_mfdataset() for automatic frequency inference."
        )

    units = time_coord.attrs["units"]
    calendar = time_coord.attrs.get("calendar", "standard")
    time_freq = time_coord.attrs["frequency"]

    # Parse units to get reference date
    ref_date = cftime.num2date(0, units, calendar, only_use_cftime_datetimes=False)

    # Calculate time range from dimension size and frequency
    total_size = ds.dims[dim]
    end_date = add_frequency(ref_date, time_freq, total_size)

    # Create time periods for grouping
    periods = create_time_periods(ref_date, end_date, freq, calendar)

    # Create subset datasets for each period
    result = []
    for period_start, period_end in periods:
        subset_ds = _create_time_subset_metadata(
            ds, period_start, period_end, dim, time_freq, calendar, normalize_units
        )
        result.append(subset_ds)

    return result


def _create_time_subset_metadata(
    ds: "DummyDataset",
    start: Any,
    end: Any,
    dim: str,
    freq: str,
    calendar: str,
    normalize_units: bool,
) -> "DummyDataset":
    """Create subset dataset using only metadata.

    Parameters
    ----------
    ds : DummyDataset
        Original dataset
    start : cftime.datetime
        Period start
    end : cftime.datetime
        Period end
    dim : str
        Time dimension
    freq : str
        Time frequency
    calendar : str
        Calendar type
    normalize_units : bool
        Whether to normalize time units

    Returns
    -------
    DummyDataset
        Subset dataset with adjusted metadata
    """
    from .core import DummyDataset

    subset_ds = DummyDataset()

    # Copy global attributes
    for key, value in ds.attrs.items():
        subset_ds.assign_attrs(**{key: value})

    # Calculate new time dimension size
    time_steps = count_timesteps(start, end, freq)

    # Add dimensions
    for dim_name, size in ds.dims.items():
        if dim_name == dim:
            subset_ds.add_dim(dim_name, time_steps)
        else:
            subset_ds.add_dim(dim_name, size)

    # Add coordinates
    for coord_name, coord_info in ds.coords.items():
        coord_attrs = coord_info.attrs.copy()

        # Update time units if normalizing
        if coord_name == dim and normalize_units:
            # Format datetime for CF units
            if hasattr(start, "strftime"):
                date_str = start.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = (
                    f"{start.year:04d}-{start.month:02d}-{start.day:02d} "
                    f"{start.hour:02d}:{start.minute:02d}:{start.second:02d}"
                )

            # Determine appropriate time unit based on frequency
            if freq.endswith("H") or freq.endswith("T") or freq.endswith("S"):
                time_unit = "hours"
            elif freq.endswith("D"):
                time_unit = "days"
            elif freq.endswith("M") or freq.endswith("Y"):
                time_unit = "days"
            else:
                time_unit = "days"

            coord_attrs["units"] = f"{time_unit} since {date_str}"

        subset_ds.add_coord(
            coord_name,
            dims=list(coord_info.dims),
            attrs=coord_attrs,
        )

    # Add variables
    for var_name, var_info in ds.variables.items():
        subset_ds.add_variable(
            var_name,
            dims=list(var_info.dims),
            attrs=var_info.attrs,
        )

    # Handle file tracking if enabled
    if hasattr(ds, "_file_tracking_enabled") and ds._file_tracking_enabled:
        subset_ds.enable_file_tracking(dim)

        # Filter file sources to this time range
        if hasattr(ds, "_file_sources"):
            for filepath, info in ds._file_sources.items():
                # For now, include all files (conservative approach)
                # In a more sophisticated implementation, we'd decode the
                # coord_range and check if it overlaps with [start, end]
                subset_ds.add_file_source(
                    filepath,
                    coord_range=info.get("coord_range"),
                    metadata=info.get("metadata", {}),
                )

    return subset_ds
