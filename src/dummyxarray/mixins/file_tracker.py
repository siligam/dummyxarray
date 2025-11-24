"""File tracking mixin for multi-file dataset support.

This module provides functionality to track source files in multi-file datasets,
enabling users to query which files contain specific coordinate ranges.
"""

from typing import Any, Dict, List, Optional, Tuple


class FileTrackerMixin:
    """Mixin for tracking source files and their coordinate ranges.

    This mixin enables DummyDataset to track which files contribute to which
    coordinate ranges, useful for multi-file datasets concatenated along a
    dimension (typically time).
    """

    def __init__(self, *args, **kwargs):
        """Initialize file tracking structures."""
        super().__init__(*args, **kwargs)
        self._file_sources: Dict[str, Dict[str, Any]] = {}
        self._concat_dim: Optional[str] = None
        self._file_tracking_enabled = False

    def enable_file_tracking(self, concat_dim: str = "time") -> None:
        """Enable tracking of source files.

        Parameters
        ----------
        concat_dim : str, optional
            The dimension along which files are concatenated (default: "time")

        Examples
        --------
        >>> ds = DummyDataset()
        >>> ds.enable_file_tracking(concat_dim="time")
        """
        self._file_tracking_enabled = True
        self._concat_dim = concat_dim
        self._file_sources = {}

    def add_file_source(
        self,
        filepath: str,
        coord_range: Tuple[Any, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a file and its coordinate coverage.

        Parameters
        ----------
        filepath : str
            Path to the source file
        coord_range : tuple of (start, end)
            The range of coordinates this file covers along concat_dim
        metadata : dict, optional
            Additional metadata about the file

        Examples
        --------
        >>> ds.add_file_source("file1.nc", coord_range=(0, 10))
        >>> ds.add_file_source("file2.nc", coord_range=(10, 20),
        ...                    metadata={"institution": "DKRZ"})
        """
        if not self._file_tracking_enabled:
            raise RuntimeError("File tracking not enabled. Call enable_file_tracking() first.")

        self._file_sources[filepath] = {
            "coord_range": coord_range,
            "concat_dim": self._concat_dim,
            "metadata": metadata or {},
        }

    def get_source_files(self, coord_slice: Optional[slice] = None, **coord_selectors) -> List[str]:
        """Get files that overlap with given coordinate ranges.

        Parameters
        ----------
        coord_slice : slice, optional
            Slice object for the concat dimension
        **coord_selectors
            Keyword arguments specifying coordinate selections
            (e.g., time=slice(5, 15))

        Returns
        -------
        list of str
            List of file paths that contain data in the specified range

        Examples
        --------
        >>> files = ds.get_source_files(time=slice(5, 15))
        >>> files = ds.get_source_files(coord_slice=slice(5, 15))
        """
        if not self._file_tracking_enabled:
            return []

        # Extract the slice for the concat dimension
        if coord_slice is None and self._concat_dim in coord_selectors:
            coord_slice = coord_selectors[self._concat_dim]

        if coord_slice is None:
            # No slice specified, return all files
            return list(self._file_sources.keys())

        # Handle different slice types
        if isinstance(coord_slice, slice):
            start = coord_slice.start
            stop = coord_slice.stop
        else:
            # Single value selection
            start = stop = coord_slice

        # Find overlapping files
        overlapping_files = []
        for filepath, info in self._file_sources.items():
            file_start, file_end = info["coord_range"]

            # Check for overlap
            if self._ranges_overlap(start, stop, file_start, file_end):
                overlapping_files.append(filepath)

        return overlapping_files

    def _ranges_overlap(
        self,
        start1: Any,
        stop1: Any,
        start2: Any,
        stop2: Any,
    ) -> bool:
        """Check if two ranges overlap.

        Parameters
        ----------
        start1, stop1 : any
            First range
        start2, stop2 : any
            Second range

        Returns
        -------
        bool
            True if ranges overlap
        """
        # Handle None values (unbounded ranges)
        if start1 is None or stop1 is None or start2 is None or stop2 is None:
            # If any bound is None, assume full overlap for simplicity
            return True

        # Try to compare directly, handling type mismatches
        try:
            # Check for overlap: ranges overlap if start1 < stop2 and start2 < stop1
            return start1 < stop2 and start2 < stop1
        except (TypeError, ValueError):
            # If comparison fails (e.g., datetime vs int), return True to be safe
            # In practice, users should query with compatible types
            return True

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get metadata about a specific file.

        Parameters
        ----------
        filepath : str
            Path to the file

        Returns
        -------
        dict
            Dictionary containing file information including coord_range and metadata

        Raises
        ------
        KeyError
            If the file is not tracked

        Examples
        --------
        >>> info = ds.get_file_info("file1.nc")
        >>> print(info["coord_range"])
        (0, 10)
        """
        if filepath not in self._file_sources:
            raise KeyError(f"File not tracked: {filepath}")

        return self._file_sources[filepath].copy()

    @property
    def file_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get all tracked file sources.

        Returns
        -------
        dict
            Dictionary mapping file paths to their metadata

        Examples
        --------
        >>> print(ds.file_sources)
        {'file1.nc': {'coord_range': (0, 10), ...}, ...}
        """
        return self._file_sources.copy()

    @property
    def is_file_tracking_enabled(self) -> bool:
        """Check if file tracking is enabled.

        Returns
        -------
        bool
            True if file tracking is enabled
        """
        return self._file_tracking_enabled

    @property
    def concat_dim(self) -> Optional[str]:
        """Get the concatenation dimension for file tracking.

        Returns
        -------
        str or None
            The dimension along which files are concatenated
        """
        return self._concat_dim
