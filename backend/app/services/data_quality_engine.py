"""Phase 1 — Data Quality Engine (Section 2 of prompt).
Treats quality as analytical dimension; generates profile per
source/entity/work; never confuses missing public data with proof data doesn't exist."""
from datetime import datetime
from typing import Dict, Any, List, Optional

class DataQualityProfile:
    def __init__(self, entity_id: str, source: str):
        self.entity_id = entity_id
        self.source = source
        self.profile_time = datetime.utcnow()
        self.issues: List[Dict[str, Any]] = []
        self.coverage_gaps = []
        self.schema_drift_notes = []

    def add_issue(self, field: str, issue_type: str, severity: str,
                  observed_value: Optional[Any], description: str):
        # severity = LOW / MEDIUM / HIGH; evidence quality separate (not fraud claim)
        self.issues.append({
            "field": field, "issue_type": issue_type, "severity": severity,
            "observed_value": str(observed_value) if observed_value is not None else None,
            "description": description, "recorded_at": datetime.utcnow().isoformat()
        })

    def check_missing_critical(self, record: Dict[str, Any], critical: List[str]):
        for f in critical:
            if not record.get(f):
                self.add_issue(f, "MISSING_CRITICAL", "HIGH",
                               record.get(f), f"Critical field '{f}' missing.")

    def check_impossible_values(self, record: Dict[str, Any]):
        # Negative amounts
        for amt_field in ["recommended_amount", "sanctioned_amount", "actual_expenditure"]:
            v = record.get(amt_field)
            if isinstance(v, (int, float)) and v < 0:
                self.add_issue(amt_field, "IMPOSSIBLE_VALUE", "HIGH", v,
                               f"Negative amount {v} in {amt_field}.")
        # Malformed dates (future dates for historical events, etc.)
        # Duplicate identifiers
        # Near-duplicate records (check against stored signatures — framework only)

    def check_inconsistent_categorical(self, record: Dict[str, Any], allowed: Dict[str, List[str]]):
        for field, valid in allowed.items():
            val = record.get(field)
            if val and str(val).strip() not in valid:
                self.add_issue(field, "INCONSISTENT_CATEGORICAL", "MEDIUM", val,
                               f"Value '{val}' not in allowed set.")

    def check_schema_drift(self, record: Dict[str, Any], expected_keys: List[str]):
        extra = [k for k in record if k not in expected_keys and not k.startswith("_")]
        missing = [k for k in expected_keys if k not in record]
        if extra: self.schema_drift_notes.append(f"Unexpected keys: {extra}")
        if missing: self.schema_drift_notes.append(f"Missing expected keys: {missing}")

    def check_duplicate_ids(self, record: Dict[str, Any], seen_ids: set):
        wid = record.get("work_id") or record.get("Work_ID")
        if wid and wid in seen_ids:
            self.add_issue("work_id", "DUPLICATE_IDENTIFIER", "HIGH", wid,
                           f"Duplicate work identifier: {wid}.")
        if wid:
            seen_ids.add(wid)

    def check_conflicting_source_values(self, records_a: List[Dict], records_b: List[Dict], key="work_id"):
        # Cross-source reconciliation framework — detects contradictions
        pass  # framework: compare A vs B, generate RECONCILIATION_CONFLICT

    def generate_profile(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id, "source": self.source,
            "profile_time": self.profile_time.isoformat(),
            "issue_count": len(self.issues),
            "issues": self.issues,
            "coverage_gaps": self.coverage_gaps,
            "schema_drift_notes": self.schema_drift_notes,
            "evidence_quality": "MEDIUM" if self.issues else "HIGH",
            "note": "Quality profile is analytical; missing fields do not prove non-existence elsewhere."
        }
