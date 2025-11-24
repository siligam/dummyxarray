"""
Random data generation for DummyDataset.

This module provides mixins for populating datasets with meaningful
random data based on metadata hints.
"""

import numpy as np


class DataGenerationMixin:
    """Mixin providing data generation capabilities."""

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
                coord_array.data = self._generate_coordinate_data(coord_name, coord_array)

        # Populate variables
        for var_name, var_array in self.variables.items():
            if var_array.data is None:
                var_array.data = self._generate_variable_data(var_name, var_array)

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
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["temperature", "temp", "tas", "ts"]
        ):
            if "k" == units or "kelvin" in units:
                # Temperature in Kelvin (250-310K range)
                return np.random.uniform(250, 310, shape)
            elif "c" == units or "celsius" in units or "degc" in units:
                # Temperature in Celsius (-30 to 40C range)
                return np.random.uniform(-30, 40, shape)
            else:
                return np.random.uniform(250, 310, shape)

        # Pressure variables (check before precipitation to avoid "pr" conflict)
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["pressure", "pres", "psl"]
        ):
            if "sea_level" in standard_name or "msl" in name.lower() or "psl" in name.lower():
                # Sea level pressure (980-1040 hPa)
                return np.random.uniform(98000, 104000, shape)
            else:
                # Generic pressure
                return np.random.uniform(50000, 105000, shape)

        # Precipitation variables
        if (
            any(
                x in standard_name or x in name.lower() or x in long_name
                for x in ["precipitation", "precip", "rain"]
            )
            or name.lower() == "pr"
        ):
            # Precipitation (always positive, skewed distribution)
            return np.random.exponential(0.001, shape)

        # Wind variables
        if any(
            x in standard_name or x in name.lower() or x in long_name for x in ["wind", "velocity"]
        ):
            # Wind speed (0-30 m/s, can be negative for components)
            if any(x in name.lower() for x in ["u", "zonal", "eastward"]):
                return np.random.uniform(-20, 20, shape)
            elif any(x in name.lower() for x in ["v", "meridional", "northward"]):
                return np.random.uniform(-20, 20, shape)
            else:
                return np.random.uniform(0, 30, shape)

        # Humidity variables
        if any(
            x in standard_name or x in name.lower() or x in long_name
            for x in ["humidity", "moisture", "rh"]
        ):
            if "relative" in standard_name or "relative" in long_name:
                # Relative humidity (0-100%)
                return np.random.uniform(20, 100, shape)
            else:
                # Specific humidity (small positive values)
                return np.random.uniform(0, 0.02, shape)

        # Radiation variables
        if any(
            x in standard_name or x in name.lower() or x in long_name for x in ["radiation", "flux"]
        ):
            # Radiation (positive values, 0-1000 W/m²)
            return np.random.uniform(0, 1000, shape)

        # Default: standard normal distribution
        return np.random.randn(*shape)
