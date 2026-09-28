"""Official MPLADS dashboard CSV adapter.

Handles the real MOSPI/eSAKSHI export:
  - semicolon-delimited
  - quoted CAPITAL field names (MP NAME, WORK, STATUS, ...)
  - no Work_ID column — stable IDs are derived from content
"""
from __future__ import annotations

import csv
import hashlib
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import DataSource


def _clean(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().strip('"')
    if text == "" or text.lower() in {"null", "none", "na", "n/a", "-"}:
        return None
    return text


def _parse_amount(value: Any) -> Optional[float]:
    text = _clean(value)
    if text is None:
        return None
    cleaned = (
        text.replace(",", "")
        .replace("₹", "")
        .replace("Rs", "")
        .replace("INR", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(value: Any) -> Optional[datetime]:
    text = _clean(value)
    if text is None:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%d/%b/%Y",
        "%d-%m-%y",
        "%Y/%m/%d",
        "%d.%m.%Y",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _financial_year(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    # Indian financial year: 1 April – 31 March
    if dt.month >= 4:
        return f"{dt.year}-{str(dt.year + 1)[2:]}"
    return f"{dt.year - 1}-{str(dt.year)[2:]}"


def _stable_work_id(parts: List[str]) -> str:
    key = "|".join(parts)
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12].upper()
    return f"MPLAD-{digest}"


class OfficialMPLADSFileAdapter(DataSource):
    """Adapter for official MPLADS manual CSV exports from the public dashboard."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.file_path = config.get("file_path")
        self.source_name = config.get("source_name", "Official MPLADS Export")
        self._source_type = config.get("source_type", "OFFICIAL_MPLADS_CSV")
        self.source_url = config.get(
            "source_url",
            "https://mplads.mospi.gov.in/digigov/dashboard.html",
        )
        self.retrieved_at = datetime.utcnow()
        self._records: Optional[List[Dict[str, Any]]] = None

    def name(self) -> str:
        return self.source_name

    def source_type(self) -> str:
        return self._source_type

    def fetch_data(self) -> List[Dict[str, Any]]:
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Official MPLADS file missing: {self.file_path}")

        self._records = []
        seen: Dict[str, int] = {}

        with open(self.file_path, "r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            delimiter = ";" if sample.count(";") > sample.count(",") else ","
            reader = csv.DictReader(handle, delimiter=delimiter)
            for index, row in enumerate(reader, start=1):
                record = self._normalize(row, index, seen)
                if record:
                    self._records.append(record)
        return self._records

    def _normalize(
        self,
        row: Dict[str, Any],
        index: int,
        seen: Dict[str, int],
    ) -> Optional[Dict[str, Any]]:
        # Official export uses spaced CAPITAL names; tolerate both.
        def get(*keys: str) -> Optional[str]:
            for key in keys:
                if key in row:
                    return _clean(row.get(key))
            # case-insensitive fallback
            lowered = {str(k).strip().lower(): v for k, v in row.items()}
            for key in keys:
                if key.lower() in lowered:
                    return _clean(lowered[key.lower()])
            return None

        description = get("WORK", "Work_Description", "work_description")
        if not description:
            return None

        mp_name = get("MP NAME", "MP_Name", "mp_name")
        constituency = get("CONSTITUENCY", "Constituency", "constituency")
        state = get("STATE", "State", "state")
        village = get("VILLAGE", "Village")
        block = get("BLOCK", "Block")
        city = get("CITY", "City")
        ward = get("WARD", "Ward")
        rec_date_raw = get("RECOMMENDED DATE", "Recommended_Date", "recommendation_date")
        amount_raw = get("ALLOCATION AMOUNT", "Recommended_Amount", "recommended_amount")
        status_raw = get("STATUS", "Status", "status")
        house = get("HOUSE", "MP_Type", "mp_type")
        agency = get("IDA", "Implementing_Agency", "implementing_agency")
        category = get("CATEGORY", "Sector", "sector")
        ida_approval = get("IDA APPROVAL", "IDA_Approval")

        rec_date = _parse_date(rec_date_raw)
        amount = _parse_amount(amount_raw)
        status = (status_raw or "").strip()
        status_upper = status.upper()

        mp_type = None
        if house:
            lowered = house.lower()
            if "lok" in lowered:
                mp_type = "Lok Sabha"
            elif "rajya" in lowered:
                mp_type = "Rajya Sabha"
            else:
                mp_type = house

        location_parts = [p for p in (village, block, ward, city, constituency, state) if p]
        location_text = ", ".join(dict.fromkeys(location_parts)) or None

        existing_id = get("Work_ID", "work_id", "WORK ID")
        if existing_id:
            work_id = existing_id
        else:
            work_id = _stable_work_id(
                [
                    mp_name or "",
                    description,
                    constituency or "",
                    rec_date_raw or "",
                    amount_raw or "",
                    village or "",
                    block or "",
                    city or "",
                    ward or "",
                    str(index),
                ]
            )
        if work_id in seen:
            seen[work_id] += 1
            work_id = f"{work_id}-{seen[work_id]}"
        else:
            seen[work_id] = 1

        is_unsanctioned = status_upper in {
            "UNSANCTIONED",
            "RECOMMENDED",
            "ACTION PENDING",
            "REJECTED",
            "CANCELLED",
        }

        return {
            "work_id": work_id,
            "source_work_id": existing_id or work_id,
            "data_source": self._source_type,
            "mp_name": mp_name,
            "mp_type": mp_type,
            "constituency": constituency,
            "state": state,
            "district": city or block,
            "financial_year": _financial_year(rec_date),
            "sector": category,
            "work_description": description,
            "implementing_agency": agency,
            "contractor_name": None,
            "location_text": location_text,
            "latitude": None,
            "longitude": None,
            "is_within_constituency": None,
            "is_sc_area": None,
            "is_st_area": None,
            "beneficiary_type": None,
            "asset_owner_type": None,
            "recommended_amount": amount,
            "sanctioned_amount": None if is_unsanctioned else amount,
            "actual_expenditure": None,
            "total_paid": None,
            "recommendation_date": rec_date,
            "sanction_date": None,
            "ia_assignment_date": None,
            "expected_completion_date": None,
            "actual_completion_date": None,
            "final_payment_date": None,
            "marked_complete_date": None,
            "status": status or None,
            "source_url": self.source_url,
            "source_last_updated": self.retrieved_at,
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_type": self._source_type,
            "source_url": self.source_url,
            "file_path": self.file_path,
            "retrieval_timestamp": self.retrieved_at.isoformat(),
            "record_count": len(self._records or []),
            "description": "Official MPLADS dashboard CSV export (verified real data)",
        }

    def validate_record(self, record: Dict[str, Any]) -> bool:
        return bool(record and record.get("work_id") and record.get("work_description"))

    def get_source_coverage(self) -> Dict[str, Any]:
        return {
            "work_id": True,
            "mp_name": True,
            "mp_type": True,
            "constituency": True,
            "state": True,
            "district": False,
            "financial_year": True,
            "sector": True,
            "work_description": True,
            "implementing_agency": True,
            "contractor_name": False,
            "location_text": True,
            "latitude": False,
            "longitude": False,
            "recommended_amount": True,
            "sanctioned_amount": True,
            "actual_expenditure": False,
            "status": True,
            "recommendation_date": True,
            "data_source": True,
            "source_url": True,
        }

    def close(self):
        self._records = None
