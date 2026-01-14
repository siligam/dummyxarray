"""
Dummy Xarray - A lightweight xarray-like object for metadata specifications.
"""

from .core import DummyArray, DummyDataset
from .ncdump_parser import from_ncdump_header

__version__ = "0.1.1"
__all__ = ["DummyArray", "DummyDataset", "from_ncdump_header"]
