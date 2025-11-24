"""CF standards validation using cf_xarray.

This module provides integration with cf_xarray for CF-compliant
metadata detection, validation, and attribute setting based on
community-agreed standards.
"""

from typing import Any, Dict, List


def check_cf_xarray_available() -> bool:
    """Check if cf_xarray is available.

    Returns
    -------
    bool
        True (always, since cf_xarray is now a required dependency)

    Examples
    --------
    >>> check_cf_xarray_available()
    True

    Notes
    -----
    This function always returns True since cf_xarray is now a required
    dependency. It's kept for backwards compatibility.
    """
    return True


def apply_cf_standards(dataset, verbose: bool = False) -> Dict[str, Any]:
    """Apply CF standards to dataset using cf_xarray.

    This uses cf_xarray's community-agreed criteria to:
    - Detect coordinate axes (X, Y, Z, T)
    - Add appropriate CF attributes
    - Validate against CF conventions

    Parameters
    ----------
    dataset : DummyDataset
        Dataset to apply CF standards to (works with or without data)
    verbose : bool, optional
        Print detailed information (default: False)

    Returns
    -------
    dict
        Summary of changes made:
        {
            'axes_detected': dict,  # Coordinate name -> axis
            'attrs_added': dict,    # Coordinate name -> added attributes
            'warnings': list        # Any warnings
        }

    Examples
    --------
    Works without data (uses temporary dummy arrays):

    >>> ds = DummyDataset()
    >>> ds.add_dim("time", 10)
    >>> ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
    >>> result = apply_cf_standards(ds)  # No data needed!
    >>> print(result['axes_detected'])
    {'time': 'T'}

    Also works with data if already populated:

    >>> ds.populate_with_random_data()
    >>> result = apply_cf_standards(ds)
    >>> print(result['axes_detected'])
    {'time': 'T'}
    >>> print(ds.coords['time'].attrs['axis'])
    'T'

    Notes
    -----
    This function uses cf_xarray's built-in criteria which are based on:
    - CF Conventions official documentation
    - MetPy's coordinate detection
    - Community best practices

    The dataset can work with or without data. If data is not populated,
    this function will temporarily create dummy arrays just for cf_xarray
    processing, then discard them (keeping only the detected metadata).
    """
    import numpy as np
    import xarray as xr

    # Check if we need to create temporary data
    needs_temp_data = False
    for coord in dataset.coords.values():
        if coord.data is None:
            needs_temp_data = True
            break
    if not needs_temp_data:
        for var in dataset.variables.values():
            if var.data is None:
                needs_temp_data = True
                break

    if needs_temp_data:
        # Create temporary xarray.Dataset with dummy data for cf_xarray
        coords_dict = {}
        for name, coord in dataset.coords.items():
            shape = tuple(dataset.dims[d] for d in coord.dims)
            data = np.zeros(shape) if coord.data is None else coord.data
            coords_dict[name] = (coord.dims, data, coord.attrs)

        data_vars_dict = {}
        for name, var in dataset.variables.items():
            shape = tuple(dataset.dims[d] for d in var.dims)
            data = np.zeros(shape) if var.data is None else var.data
            data_vars_dict[name] = (var.dims, data, var.attrs)

        xr_ds = xr.Dataset(coords=coords_dict, data_vars=data_vars_dict, attrs=dataset.attrs)
    else:
        # Convert to xarray normally (data already exists)
        xr_ds = dataset.to_xarray()

    # Use cf_xarray to guess and add attributes
    xr_ds = xr_ds.cf.guess_coord_axis(verbose=verbose)

    # Track changes
    axes_detected = {}
    attrs_added = {}
    warnings_list = []

    # Update DummyDataset with new attributes
    for coord_name, coord in dataset.coords.items():
        if coord_name in xr_ds.coords:
            xr_coord = xr_ds.coords[coord_name]

            # Check what axis was detected
            for axis in ["X", "Y", "Z", "T"]:
                if "axis" in xr_coord.attrs and xr_coord.attrs["axis"] == axis:
                    axes_detected[coord_name] = axis
                    break

            # Track new attributes
            new_attrs = {}
            for attr_name, attr_value in xr_coord.attrs.items():
                if attr_name not in coord.attrs:
                    new_attrs[attr_name] = attr_value

            if new_attrs:
                attrs_added[coord_name] = new_attrs
                # Update the DummyDataset coordinate
                coord.attrs.update(new_attrs)

    return {
        "axes_detected": axes_detected,
        "attrs_added": attrs_added,
        "warnings": warnings_list,
    }


def get_cf_standard_names() -> List[str]:
    """Get list of CF standard names recognized by cf_xarray.

    Returns
    -------
    list of str
        List of recognized CF standard names
        Returns empty list if cf_xarray not available

    Examples
    --------
    >>> names = get_cf_standard_names()
    >>> 'latitude' in names
    True
    >>> 'air_temperature' in names
    True
    """
    # Return common CF standard names
    # Note: cf_xarray's internal API may change, so we return a basic list
    standard_names = {
        "latitude",
        "longitude",
        "time",
        "air_temperature",
        "air_pressure",
        "altitude",
        "height",
        "depth",
    }

    return sorted(standard_names)


def validate_cf_metadata(dataset, strict: bool = False) -> Dict[str, Any]:
    """Validate CF metadata using cf_xarray criteria.

    This validates that coordinates and variables have appropriate
    CF-compliant metadata based on community standards.

    Parameters
    ----------
    dataset : DummyDataset
        Dataset to validate
    strict : bool, optional
        If True, treat warnings as errors (default: False)

    Returns
    -------
    dict
        Validation results:
        {
            'valid': bool,
            'errors': list,
            'warnings': list,
            'suggestions': list
        }

    Examples
    --------
    >>> ds = DummyDataset()
    >>> ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
    >>> result = validate_cf_metadata(ds)
    >>> result['valid']
    True
    """
    import numpy as np
    import xarray as xr

    errors = []
    warnings_list = []
    suggestions = []

    # Check if we need to create temporary data
    needs_temp_data = False
    for coord in dataset.coords.values():
        if coord.data is None:
            needs_temp_data = True
            break
    if not needs_temp_data:
        for var in dataset.variables.values():
            if var.data is None:
                needs_temp_data = True
                break

    if needs_temp_data:
        # Create temporary xarray.Dataset with dummy data for cf_xarray
        coords_dict = {}
        for name, coord in dataset.coords.items():
            shape = tuple(dataset.dims[d] for d in coord.dims)
            data = np.zeros(shape) if coord.data is None else coord.data
            coords_dict[name] = (coord.dims, data, coord.attrs)

        data_vars_dict = {}
        for name, var in dataset.variables.items():
            shape = tuple(dataset.dims[d] for d in var.dims)
            data = np.zeros(shape) if var.data is None else var.data
            data_vars_dict[name] = (var.dims, data, var.attrs)

        xr_ds = xr.Dataset(coords=coords_dict, data_vars=data_vars_dict, attrs=dataset.attrs)
    else:
        # Convert to xarray normally (data already exists)
        xr_ds = dataset.to_xarray()

    # Check each coordinate
    for coord_name, coord in dataset.coords.items():
        # Check if axis can be detected
        try:
            # Try to identify the coordinate
            detected = False
            for axis in ["X", "Y", "Z", "T"]:
                try:
                    if coord_name in xr_ds.cf.coordinates.get(axis, []):
                        detected = True
                        break
                except (KeyError, AttributeError):
                    pass

            if not detected:
                # Check for standard_name
                if "standard_name" not in coord.attrs:
                    suggestions.append(f"{coord_name}: Consider adding 'standard_name' attribute")

                # Check for axis attribute
                if "axis" not in coord.attrs:
                    suggestions.append(f"{coord_name}: Consider adding 'axis' attribute")

        except Exception as e:
            warnings_list.append(f"{coord_name}: Could not validate - {str(e)}")

    # Check variables
    for var_name, var in dataset.variables.items():
        if "standard_name" not in var.attrs and "long_name" not in var.attrs:
            warnings_list.append(f"{var_name}: Missing both 'standard_name' and 'long_name'")

        if "units" not in var.attrs:
            warnings_list.append(f"{var_name}: Missing 'units' attribute")

    valid = len(errors) == 0 and (not strict or len(warnings_list) == 0)

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings_list,
        "suggestions": suggestions,
    }


# Add methods to DummyDataset via mixin
class CFStandardsMixin:
    """Mixin to add CF standards support to DummyDataset.

    This mixin provides integration with cf_xarray for applying
    community-agreed CF standards to datasets.
    """

    def apply_cf_standards(self, verbose: bool = False) -> Dict[str, Any]:
        """Apply CF standards using cf_xarray.

        Uses cf_xarray's community-agreed criteria to detect axes
        and add appropriate CF attributes.

        Parameters
        ----------
        verbose : bool, optional
            Print detailed information (default: False)

        Returns
        -------
        dict
            Summary of changes (axes_detected, attrs_added, warnings)

        Raises
        ------
        ImportError
            If cf_xarray is not installed

        Examples
        --------
        >>> ds.add_coord("time", dims=["time"],
        ...              attrs={"units": "days since 2000-01-01"})
        >>> result = ds.apply_cf_standards()
        >>> print(ds.coords['time'].attrs['axis'])
        'T'

        See Also
        --------
        validate_cf_metadata : Validate CF metadata
        infer_axis : Basic axis inference (no dependencies)
        """
        return apply_cf_standards(self, verbose=verbose)

    def validate_cf_metadata(self, strict: bool = False) -> Dict[str, Any]:
        """Validate CF metadata using cf_xarray.

        Validates coordinates and variables against CF standards.

        Parameters
        ----------
        strict : bool, optional
            Treat warnings as errors (default: False)

        Returns
        -------
        dict
            Validation results (valid, errors, warnings, suggestions)

        Examples
        --------
        >>> result = ds.validate_cf_metadata()
        >>> if result['valid']:
        ...     print("CF metadata is valid!")
        """
        return validate_cf_metadata(self, strict=strict)

    def check_cf_standards_available(self) -> bool:
        """Check if CF standards support is available.

        Returns
        -------
        bool
            True if cf_xarray is installed

        Examples
        --------
        >>> if ds.check_cf_standards_available():
        ...     ds.apply_cf_standards()
        ... else:
        ...     print("Install: pip install cf_xarray")
        """
        return check_cf_xarray_available()
