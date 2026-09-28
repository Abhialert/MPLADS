"""Phase 2 (partial) — Reconciliation + Evidence Graph framework (Section 12, Section 13).
Detects cross-source conflicts (status, amounts, dates). Records evidence lineage
from finding -> detector/version -> feature/calculation -> entity -> source snapshot.
No fabricated data; conflicts are analytical signals for reviewer."""
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class ReconciliationConflict:
    """Represents a detected conflict between independently available records (Section 12)."""
    def __init__(self, work_id: str):
        self.work_id = work_id
        self.conflicts: List[Dict[str, Any]] = []

    def add_conflict(self, field: str, source_a: str, value_a: Any, source_b: str, value_b: Any, reason: str):
        self.conflicts.append({
            "field": field,
            "source_a": {"source": source_a, "value": str(value_a) if value_a else None},
            "source_b": {"source": source_b, "value": str(value_b) if value_b else None},
            "conflict_type": "RECONCILIATION_CONFLICT",
            "reason": reason,
            "severity": "HIGH",
            "detected_at": datetime.utcnow().isoformat(),
            "review_status": "OPEN"
        })

    def to_evidence(self) -> Dict[str, Any]:
        return {
            "finding_id": f"RECON-{self.work_id}-{len(self.conflicts)}",
            "work_id": self.work_id,
            "conflicts": self.conflicts,
            "evidence_quality": "MEDIUM",  # depends on source trust
            "note": "Cross-source contradictions are analytical; reviewer must verify."
        }

class EvidenceGraph:
    """Traces every finding back to source snapshot (Section 13).
    finding -> detector/version -> feature/calculation -> canonical entity
    -> source snapshot -> original value."""
    def __init__(self):
        self.edges: Dict[str, Dict[str, Any]] = {}

    def add_finding(self, finding_id: str, work_id: str, detector_id: str,
                    detector_version: str, feature_calc: str):
        self.edges[finding_id] = {
            "finding_id": finding_id,
            "work_id": work_id,
            "detector_id": detector_id,
            "detector_version": detector_version,
            "feature_calculation": feature_calc,
            "timestamp": datetime.utcnow().isoformat(),
            "source_records": [],
            "original_values": [],
            "traced": False
        }

    def link_to_source(self, finding_id: str, source_snapshot_id: str, original_value: Any, canonical_field: str):
        if finding_id in self.edges:
            self.edges[finding_id]["source_records"].append({
                "snapshot_id": source_snapshot_id, "canonical_field": canonical_field, "original_value": str(original_value)
            })

    def trace(self, finding_id: str) -> Optional[Dict[str, Any]]:
        """Full lineage chain — reviewer can reproduce the reasoning."""
        return self.edges.get(finding_id)

def compare_amounts(value_a: Any, value_b: Any) -> bool:
    """Helper: compares numeric amounts; returns True if conflict."""
    try:
        return abs(float(value_a) - float(value_b)) > 0.01
    except (TypeError, ValueError):
        return value_a != value_b if value_a and value_b else False

def reconcile_works(records_a: List[Dict[str, Any]], records_b: List[Dict[str, Any]],
                    source_name_a: str, source_name_b: str) -> List[Dict[str, Any]]:
    """Compare two source record sets by work_id; detect contradictions."""
    conflicts = []
    by_id_a = {r.get("work_id"): r for r in records_a if r.get("work_id")}
    by_id_b = {r.get("work_id"): r for r in records_b if r.get("work_id")}

    for wid in set(by_id_a.keys()) & set(by_id_b.keys()):
        ra, rb = by_id_a[wid], by_id_b[wid]
        rc = ReconciliationConflict(wid)

        # Status conflict
        if ra.get("status") and rb.get("status") and ra.get("status") != rb.get("status"):
            rc.add_conflict("status", source_name_a, ra.get("status"), source_name_b, rb.get("status"),
                            "Contradictory status between sources.")

        # Amount conflict
        for amt_field in ["recommended_amount", "sanctioned_amount", "actual_expenditure"]:
            va, vb = ra.get(amt_field), rb.get(amt_field)
            if va and vb and compare_amounts(va, vb):
                rc.add_conflict(amt_field, source_name_a, va, source_name_b, vb,
                                "Conflicting monetary amounts.")

        # Date conflict (start > completion reversal)
        for date_pair in [("recommendation_date", "actual_completion_date"), ("sanction_date", "actual_completion_date")]:
            d1, d2 = ra.get(date_pair[0]), ra.get(date_pair[1])
            if d1 and d2 and d1 > d2:
                rc.add_conflict(date_pair[0], source_name_a, d1, "none", None,
                                f"Date order violation: {date_pair[0]} > {date_pair[1]}.")

        if rc.conflicts:
            conflicts.append(rc.to_evidence())

    return conflicts

class ReviewPriority:
    """Phase 15 — Review priority (NOT fraud probability).
    Combines severity, evidence strength, independent signals, materiality."""
    @staticmethod
    def compute(priority_inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Component inputs preserved (no black-box collapse)
        severity = priority_inputs.get("severity_signals", [])
        evidence_strength = priority_inputs.get("evidence_quality", "MEDIUM")
        num_signals = len(priority_inputs.get("independent_signals", []))
        materiality = priority_inputs.get("materiality", "LOW")

        score = 0
        if any(s == "HIGH" for s in severity): score += 3
        if evidence_strength == "HIGH": score += 2
        if evidence_strength == "MEDIUM": score += 1
        if num_signals >= 3: score += 2
        elif num_signals >= 1: score += 1
        if materiality == "HIGH": score += 2

        level = "HIGH" if score >= 5 else "MEDIUM" if score >= 3 else "LOW"
        return {
            "review_priority": level,
            "score": score,
            "evidence_quality": evidence_strength,
            "num_independent_signals": num_signals,
            "materiality": materiality,
            "component_reasons": {
                "severity_signals": severity,
                "independent_signals": priority_inputs.get("independent_signals", []),
                "note": "Priority is a review signal, not a fraud probability."
            }
        }
