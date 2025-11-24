"""
CF compliance and axis detection for DummyDataset.

This module provides mixins for CF convention validation and automatic
axis detection (X/Y/Z/T) based on coordinate metadata.
"""


class CFComplianceMixin:
    """Mixin providing CF compliance and axis detection capabilities."""

    def infer_axis(self, coord_name=None):
        """
        Infer axis attribute (X/Y/Z/T) for coordinates based on CF conventions.

        Uses coordinate names, standard_name attributes, units, and dimension
        patterns to automatically detect axis types.

        Parameters
        ----------
        coord_name : str, optional
            Specific coordinate to infer axis for. If None, infers for all coordinates.

        Returns
        -------
        dict
            Dictionary mapping coordinate names to inferred axis values ('X', 'Y', 'Z', 'T')

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_dim("lat", 64)
        >>> ds.add_dim("lon", 128)
        >>> ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        >>> ds.add_coord("lat", dims=["lat"], attrs={"units": "degrees_north"})
        >>> ds.add_coord("lon", dims=["lon"], attrs={"units": "degrees_east"})
        >>> axes = ds.infer_axis()
        >>> # Returns: {'time': 'T', 'lat': 'Y', 'lon': 'X'}
        """
        axes = {}
        coords_to_check = [coord_name] if coord_name else list(self.coords.keys())

        for name in coords_to_check:
            if name not in self.coords:
                continue

            coord = self.coords[name]
            axis = self._detect_axis_type(name, coord)
            if axis:
                axes[name] = axis

        return axes

    def _detect_axis_type(self, name, coord):
        """
        Detect axis type for a coordinate based on CF conventions.

        Parameters
        ----------
        name : str
            Coordinate name
        coord : DummyArray
            Coordinate object

        Returns
        -------
        str or None
            Axis type ('X', 'Y', 'Z', 'T') or None if cannot be determined
        """
        # Check if axis already set
        if coord.attrs.get("axis"):
            return coord.attrs["axis"]

        # Check standard_name (CF convention)
        standard_name = coord.attrs.get("standard_name", "").lower()
        standard_name_map = {
            "longitude": "X",
            "projection_x_coordinate": "X",
            "grid_longitude": "X",
            "latitude": "Y",
            "projection_y_coordinate": "Y",
            "grid_latitude": "Y",
            "altitude": "Z",
            "height": "Z",
            "depth": "Z",
            "air_pressure": "Z",
            "model_level_number": "Z",
            "time": "T",
        }
        if standard_name in standard_name_map:
            return standard_name_map[standard_name]

        # Check units (CF convention)
        units = coord.attrs.get("units", "").lower()

        # Time axis patterns
        time_patterns = ["since", "days", "hours", "minutes", "seconds"]
        if any(pattern in units for pattern in time_patterns):
            return "T"

        # Longitude patterns
        if units in ["degrees_east", "degree_east", "degreee", "degreese"]:
            return "X"

        # Latitude patterns
        if units in ["degrees_north", "degree_north", "degreen", "degreesn"]:
            return "Y"

        # Vertical coordinate patterns
        vertical_units = ["pa", "hpa", "mbar", "bar", "m", "km", "level", "sigma", "eta"]
        if any(units.startswith(u) for u in vertical_units):
            return "Z"

        # Check coordinate name patterns (common conventions)
        name_lower = name.lower()

        # X-axis patterns
        x_patterns = ["lon", "longitude", "x", "i", "ni", "xc"]
        if any(name_lower.startswith(p) or name_lower == p for p in x_patterns):
            return "X"

        # Y-axis patterns
        y_patterns = ["lat", "latitude", "y", "j", "nj", "yc"]
        if any(name_lower.startswith(p) or name_lower == p for p in y_patterns):
            return "Y"

        # Z-axis patterns
        z_patterns = ["lev", "level", "plev", "height", "depth", "alt", "z", "k", "nk"]
        if any(name_lower.startswith(p) or name_lower == p for p in z_patterns):
            return "Z"

        # T-axis patterns
        t_patterns = ["time", "t", "date"]
        if any(name_lower.startswith(p) or name_lower == p for p in t_patterns):
            return "T"

        return None

    def set_axis_attributes(self, inferred_only=False):
        """
        Set axis attributes on coordinates based on inferred axis types.

        This modifies coordinate attributes in-place to add 'axis' attributes
        following CF conventions.

        Parameters
        ----------
        inferred_only : bool, default False
            If True, only set axis for coordinates that don't already have one.
            If False, overwrite existing axis attributes with inferred values.

        Returns
        -------
        dict
            Dictionary of coordinate names and their assigned axis values

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"], attrs={"units": "days since 2000-01-01"})
        >>> ds.set_axis_attributes()
        >>> print(ds.coords["time"].attrs["axis"])
        T
        """
        assigned = {}

        for coord_name, coord in self.coords.items():
            # Check if we should skip this coordinate
            if inferred_only and "axis" in coord.attrs:
                continue

            # Temporarily remove axis attribute to force re-inference
            existing_axis = coord.attrs.pop("axis", None)

            # Infer axis for this coordinate
            axis = self._detect_axis_type(coord_name, coord)

            if axis:
                # Set the inferred axis attribute
                coord.attrs["axis"] = axis
                assigned[coord_name] = axis
            elif existing_axis:
                # Restore existing axis if we couldn't infer a new one
                coord.attrs["axis"] = existing_axis

        return assigned

    def get_axis_coordinates(self, axis):
        """
        Get all coordinates with a specific axis attribute.

        Parameters
        ----------
        axis : str
            Axis type to search for ('X', 'Y', 'Z', 'T')

        Returns
        -------
        list
            List of coordinate names with the specified axis

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_coord("lon", dims=["lon"], attrs={"axis": "X"})
        >>> ds.add_coord("lat", dims=["lat"], attrs={"axis": "Y"})
        >>> x_coords = ds.get_axis_coordinates("X")
        >>> # Returns: ['lon']
        """
        coords = []
        for name, coord in self.coords.items():
            if coord.attrs.get("axis") == axis:
                coords.append(name)
        return coords

    def validate_cf(self, strict=False):
        """
        Validate dataset against CF conventions.

        Checks for common CF compliance issues like missing axis attributes,
        invalid units, missing standard_name, etc.

        Parameters
        ----------
        strict : bool, default False
            If True, raise ValueError on any CF violation.
            If False, return a list of warnings/errors.

        Returns
        -------
        dict
            Dictionary with 'errors' and 'warnings' lists

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.add_dim("time", 10)
        >>> ds.add_coord("time", dims=["time"])
        >>> result = ds.validate_cf()
        >>> print(result['warnings'])
        ['time: Missing axis attribute', 'time: Missing units attribute']
        """
        errors = []
        warnings = []

        # Check coordinates for axis attributes
        for name, coord in self.coords.items():
            # Check for axis attribute
            if "axis" not in coord.attrs:
                inferred = self.infer_axis(name)
                if name in inferred:
                    warnings.append(
                        f"{name}: Missing 'axis' attribute (can be inferred as '{inferred[name]}')"
                    )
                else:
                    warnings.append(f"{name}: Missing 'axis' attribute (cannot infer)")

            # Check for units
            if "units" not in coord.attrs:
                warnings.append(f"{name}: Missing 'units' attribute")

            # Check for standard_name on coordinates
            if "standard_name" not in coord.attrs:
                warnings.append(f"{name}: Missing 'standard_name' attribute")

        # Check variables for required attributes
        for name, var in self.variables.items():
            # Check for units
            if "units" not in var.attrs:
                warnings.append(f"{name}: Variable missing 'units' attribute")

            # Check for long_name or standard_name
            if "long_name" not in var.attrs and "standard_name" not in var.attrs:
                warnings.append(f"{name}: Variable missing both 'long_name' and 'standard_name'")

        # Check global attributes
        required_global = ["Conventions"]
        for attr in required_global:
            if attr not in self.attrs:
                warnings.append(f"Missing required global attribute: '{attr}'")

        # Check for CF Conventions version
        if "Conventions" in self.attrs:
            conventions = self.attrs["Conventions"]
            if not any(cf in conventions for cf in ["CF-", "cf-"]):
                warnings.append(f"Conventions attribute '{conventions}' does not reference CF")

        # Check dimension ordering (CF recommends T, Z, Y, X)
        for name, var in self.variables.items():
            if var.dims and len(var.dims) > 1:
                # Get axis types for dimensions
                dim_axes = []
                for dim in var.dims:
                    if dim in self.coords:
                        axis = self.coords[dim].attrs.get("axis")
                        if axis:
                            dim_axes.append(axis)

                # Check if order is T, Z, Y, X
                expected_order = ["T", "Z", "Y", "X"]
                actual_order = [a for a in dim_axes if a in expected_order]
                sorted_order = sorted(actual_order, key=lambda x: expected_order.index(x))

                if actual_order != sorted_order:
                    warnings.append(
                        f"{name}: Dimension order {actual_order} does not follow "
                        f"CF recommendation (T, Z, Y, X)"
                    )

        result = {"errors": errors, "warnings": warnings}

        if strict and (errors or warnings):
            all_issues = errors + warnings
            raise ValueError("CF validation failed:\n" + "\n".join(all_issues))

        return result
