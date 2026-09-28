"""Base DataSource abstract class for MPLAD Integrity Engine adapters."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class DataSource(ABC):
    """Abstract base class for all data source adapters."""

    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data source with configuration.

        Args:
            config: Dictionary containing source configuration
                   (e.g., source_name, source_type, source_url, credentials)
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of this data source."""
        pass

    @abstractmethod
    def source_type(self) -> str:
        """Return the type of data source (e.g., 'real', 'synthetic', 'official')."""
        pass

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the source.

        Returns:
            List of dictionaries, where each dictionary represents a record
            with keys matching canonical field names.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the data source.

        Returns:
            Dictionary containing metadata such as:
            - source_url
            - source_type
            - source_name
            - version
            - retrieval_timestamp
            - record_count
            - description
        """
        pass

    @abstractmethod
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a single record.

        Args:
            record: Dictionary representing a data record

        Returns:
            True if the record is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_source_coverage(self) -> Dict[str, Any]:
        """
        Get information about which fields are available from this source.

        Returns:
            Dictionary mapping canonical field names to their availability status:
            - True: field is available
            - False: field is not available
            - None: availability unknown
        """
        pass

    @abstractmethod
    def close(self):
        """Clean up any resources held by the adapter."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()