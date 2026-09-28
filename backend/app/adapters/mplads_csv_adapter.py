"""MPLADS CSV Adapter for the real 60k-record official export.
Extends EsakshiCSVAdapter with field mapping for the official
MPLADS dashboard CSV (semicolon-delimited, CAPITAL_WITH_UNDERSCORE fields).
"""
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from .esakshi_adapter import EsakshiCSVAdapter

class MPLADSCSVAdapter(EsakshiCSVAdapter):
    """Adapter for official MPLADS CSV export (60k+ records)."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._source_name = config.get("source_name", "MPLADS Official CSV Export")
        self._source_type = config.get("source_type", "OFFICIAL_MPLADS_CSV")
        self._field_mapping = self._get_field_mapping()

    def _get_field_mapping(self) -> Dict[str, str]:
        """Map official MPLADS CSV fields to canonical names."""
        return {
            "MP NAME": "mp_name",
            "WORK": "work_description",
            "CATEGORY": "category",
            "STATE": "state",
            "CONSTITUENCY": "constituency",
            "HOUSE": "mp_type",
            "IDA": "implementing_agency",
            "IDA APPROVAL": "ida_approval_status",
            "RECOMMENDED DATE": "recommendation_date",
            "ALLOCATION AMOUNT": "recommended_amount",
            "STATUS": "status",
            "BLOCK": "block",
            "VILLAGE": "village",
            "CITY": "city",
            "WARD": "ward",
        }

    def _normalize_record(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a record from official MPLADS CSV."""
        if not row or not row.get("WORK"):
            return None
        normalized = super()._normalize_record(row)
        # Add MP type normalization
        if normalized and normalized.get("mp_type"):
            mp_type = normalized["mp_type"].strip().lower()
            if "lok" in mp_type:
                normalized["mp_type"] = "Lok Sabha"
            elif "rajya" in mp_type:
                normalized["mp_type"] = "Rajya Sabha"
        return normalized
