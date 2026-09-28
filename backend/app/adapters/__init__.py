"""Source adapters for MPLAD Integrity Engine."""
from .base import DataSource
from .esakshi_adapter import EsakshiCSVAdapter, EsakshiAPIAdapter
from .official_mplads_adapter import OfficialMPLADSFileAdapter

__all__ = [
    "DataSource",
    "EsakshiCSVAdapter",
    "EsakshiAPIAdapter",
    "OfficialMPLADSFileAdapter",
]