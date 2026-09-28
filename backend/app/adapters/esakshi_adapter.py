"""eSAKSHI CSV/JSON Adapter for MPLAD Integrity Engine."""

import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from .base import DataSource


class EsakshiCSVAdapter(DataSource):
    """Adapter for eSAKSHI public CSV/JSON export data."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the eSAKSHI CSV adapter.

        Args:
            config: Configuration dictionary containing:
                - file_path: Path to CSV/JSON file
                - source_name: Name for this data source
                - source_type: Type identifier (e.g., 'esakshi_public_export')
                - source_url: URL where data was obtained
        """
        self.config = config
        self._file_path = config.get("file_path")
        self._source_name = config.get("source_name", "eSAKSHI Public Export")
        self._source_type = config.get("source_type", "REAL_ESAKSHI")
        self._source_url = config.get("source_url", "https://mplads.mospi.gov.in/digigov/dashboard.html")
        self._retrieval_time = datetime.utcnow()
        self._records = None
        self._field_mapping = self._get_field_mapping()

    def _get_field_mapping(self) -> Dict[str, str]:
        """Map eSAKSHI export field names to canonical field names."""
        return {
            "Work_ID": "work_id",
            "MP_Name": "mp_name",
            "MP_Type": "mp_type",
            "Constituency": "constituency",
            "State": "state",
            "Financial_Year": "financial_year",
            "Work_Description": "work_description",
            "Recommended_Amount": "recommended_amount",
            "Sanctioned_Amount": "sanctioned_amount",
            "Actual_Expenditure": "actual_expenditure",
            "Recommended_Date": "recommendation_date",
            "Sanction_Date": "sanction_date",
            "Completion_Date": "actual_completion_date",
            "Status": "status",
            "Implementing_Agency": "implementing_agency",
            "Location_Text": "location_text",
            "Source_URL": "source_url",
        }

    def name(self) -> str:
        return self._source_name

    def source_type(self) -> str:
        return self._source_type

    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Load and parse the CSV/JSON file.

        Returns:
            List of normalized work records.
        """
        if not self._file_path or not os.path.exists(self._file_path):
            raise FileNotFoundError(f"Data file not found: {self._file_path}")

        self._records = []
        ext = os.path.splitext(self._file_path)[1].lower()

        if ext == ".csv":
            with open(self._file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    normalized = self._normalize_record(row)
                    if normalized:
                        self._records.append(normalized)
        elif ext == ".json":
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for row in data:
                    normalized = self._normalize_record(row)
                    if normalized:
                        self._records.append(normalized)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        return self._records

    def _normalize_record(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a single record from eSAKSHI export to canonical format."""
        if not row:
            return None

        normalized = {}

        # Apply field mapping
        for export_field, canonical_field in self._field_mapping.items():
            value = row.get(export_field)
            normalized[canonical_field] = self._clean_value(value)

        # Set default/source fields
        normalized["data_source"] = self._source_type
        normalized["source_work_id"] = normalized.get("work_id")
        normalized["source_last_updated"] = self._retrieval_time
        normalized["source_url"] = normalized.get("source_url") or self._source_url
        normalized["created_at"] = datetime.utcnow()
        normalized["updated_at"] = datetime.utcnow()

        # Parse amounts (handle Indian number formats)
        for amount_field in ["recommended_amount", "sanctioned_amount", "actual_expenditure"]:
            if normalized.get(amount_field):
                normalized[amount_field] = self._parse_amount(normalized[amount_field])

        # Parse dates
        for date_field in ["recommendation_date", "sanction_date", "actual_completion_date"]:
            if normalized.get(date_field):
                normalized[date_field] = self._parse_date(normalized[date_field])

        # Normalize MP type
        if normalized.get("mp_type"):
            mp_type = normalized["mp_type"].strip().lower()
            if "lok" in mp_type:
                normalized["mp_type"] = "Lok Sabha"
            elif "rajya" in mp_type:
                normalized["mp_type"] = "Rajya Sabha"

        # Normalize status
        if normalized.get("status"):
            normalized["status"] = normalized["status"].strip().upper()

        return normalized

    def _clean_value(self, value: Any) -> Any:
        """Clean a raw value from the export."""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value == "" or value.lower() in ["null", "none", "na", "n/a", "-"]:
                return None
        return value

    def _parse_amount(self, value: Any) -> Optional[float]:
        """Parse amount values, handling Indian number formats (e.g., '1,23,456.78')."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove commas and currency symbols
            cleaned = value.replace(",", "").replace("₹", "").replace("Rs", "").replace("INR", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse date values from various formats."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            formats = [
                "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y",
                "%d/%b/%Y", "%d-%m-%y", "%Y/%m/%d", "%d.%m.%Y"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value.strip(), fmt)
                except ValueError:
                    continue
        return None

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_name": self._source_name,
            "source_type": self._source_type,
            "source_url": self._source_url,
            "file_path": self._file_path,
            "retrieval_timestamp": self._retrieval_time.isoformat(),
            "record_count": len(self._records) if self._records else 0,
            "description": "eSAKSHI public dashboard CSV/JSON export"
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a single work record."""
        if not record:
            return False
        # Must have a work ID
        if not record.get("work_id"):
            return False
        return True

    def get_source_coverage(self) -> Dict[str, Any]:
        """Return which canonical fields are available from this source."""
        return {
            "work_id": True,
            "source_work_id": True,
            "data_source": True,
            "mp_name": True,
            "mp_type": True,
            "constituency": True,
            "state": True,
            "district": False,
            "financial_year": True,
            "sector": False,
            "work_description": True,
            "implementing_agency": True,
            "contractor_name": False,
            "location_text": True,
            "latitude": False,
            "longitude": False,
            "is_within_constituency": False,
            "is_sc_area": False,
            "is_st_area": False,
            "beneficiary_type": False,
            "asset_owner_type": False,
            "recommended_amount": True,
            "sanctioned_amount": True,
            "actual_expenditure": True,
            "total_paid": False,
            "recommendation_date": True,
            "sanction_date": True,
            "ia_assignment_date": False,
            "expected_completion_date": False,
            "actual_completion_date": True,
            "final_payment_date": False,
            "marked_complete_date": False,
            "status": True,
            "source_url": True,
            "source_last_updated": True,
        }

    def close(self):
        """Clean up resources."""
        self._records = None


class EsakshiAPIAdapter(DataSource):
    """Placeholder for future eSAKSHI API adapter (if stable public API is verified)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._source_name = config.get("source_name", "eSAKSHI Public API")
        self._source_type = config.get("source_type", "REAL_ESAKSHI")
        self._source_url = config.get("source_url", "https://mplads.mospi.gov.in/digigov/dashboard.html")

    def name(self) -> str:
        return self._source_name

    def source_type(self) -> str:
        return self._source_type

    def fetch_data(self) -> List[Dict[str, Any]]:
        raise NotImplementedError(
            "eSAKSHI public API adapter not implemented. "
            "Use EsakshiCSVAdapter for CSV/JSON exports instead."
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_name": self._source_name,
            "source_type": self._source_type,
            "source_url": self._source_url,
            "status": "not_implemented"
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        return False

    def get_source_coverage(self) -> Dict[str, Any]:
        return {}

    def close(self):
        pass