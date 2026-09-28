"""Phase 2 (partial) — Investigation Assistant (Section 18).
For every finding automatically generates:
What happened? Why detected? Evidence supporting it? Evidence missing?
What should be checked? What changed over time?
No fabricated conclusions; outputs are actionable review prompts."""
from datetime import datetime
from typing import Dict, Any, List, Optional

class InvestigationAssistant:
    """Generates structured investigation prompts from detector findings."""
    def __init__(self, work: Dict[str, Any]):
        self.work = work
        self.findings: List[Dict[str, Any]] = []
        self.snapshots: List[Dict[str, Any]] = []

    def add_finding(self, finding: Dict[str, Any]):
        self.findings.append(finding)

    def add_snapshot(self, snap: Dict[str, Any]):
        self.snapshots.append(snap)

    def build_report(self) -> Dict[str, Any]:
        return {
            "work_id": self.work.get("work_id"),
            "work_description": self.work.get("work_description"),
            "generated_at": datetime.utcnow().isoformat(),
            "what_happened": self._what_happened(),
            "why_detected": self._why_detected(),
            "evidence_supporting": self._evidence_supporting(),
            "evidence_missing": self._evidence_missing(),
            "what_should_be_checked": self._what_should_be_checked(),
            "what_changed_over_time": self._what_changed_over_time(),
            "note": "This is a review prompt, not a conclusion. Human verification required."
        }

    def _what_happened(self) -> str:
        if not self.findings:
            return "No anomalies detected for this work."
        return "; ".join([f.get("explanation", str(f)) for f in self.findings])

    def _why_detected(self) -> str:
        if not self.findings:
            return "No detector signals."
        return "; ".join([f.get("reason", f.get("detector_id", "unknown")) for f in self.findings])

    def _evidence_supporting(self) -> List[Dict[str, Any]]:
        return [
            {"detector_id": f.get("detector_id"), "observed_value": f.get("observed_value"),
             "reference_value": f.get("reference_value"), "source_fields": f.get("source_fields")}
            for f in self.findings
        ]

    def _evidence_missing(self) -> List[str]:
        missing = []
        for f in self.findings:
            for mf in f.get("missing_fields", []):
                missing.append(f"{mf} (required by {f.get('detector_id')})")
        return list(set(missing))

    def _what_should_be_checked(self) -> List[str]:
        actions = []
        for f in self.findings:
            det = f.get("detector_id", "")
            if det == "COST_ANOMALY":
                actions.append("Verify payment records and work progress for this work.")
            elif det == "TIMELINE_ANOMALY":
                actions.append("Request site visit and contractor review.")
            elif det == "POTENTIAL_DUPLICATE":
                actions.append("Verify beneficiary and location for this work.")
            elif det == "DATA_QUALITY_AUDITOR":
                actions.append("Request missing documentation from District Authority.")
            elif det == "GEOGRAPHIC_COMPLIANCE":
                actions.append("Verify work location against constituency boundary.")
            elif det == "SC_ST_QUOTA":
                actions.append("Review SC/ST fund allocation against guidelines.")
        return list(dict.fromkeys(actions))

    def _what_changed_over_time(self) -> List[Dict[str, Any]]:
        return self.snapshots


class ReviewWorkflow:
    """Human-in-the-Loop (Section 16).
    States: OPEN / UNDER_REVIEW / EXPLAINED / RECONCILED / ESCALATED / DISMISSED_WITH_REASON."""
    STATES = ["OPEN", "UNDER_REVIEW", "EXPLAINED", "RECONCILED", "ESCALATED", "DISMISSED_WITH_REASON"]

    def __init__(self, finding_id: str):
        self.finding_id = finding_id
        self.state = "OPEN"
        self.history: List[Dict[str, Any]] = []

    def transition(self, new_state: str, reviewer: str, explanation: str, evidence_added: str = None,
                   detector_version: str = None):
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "reviewer": reviewer,
            "state": new_state,
            "explanation": explanation,
            "evidence_added": evidence_added,
            "detector_version": detector_version,
            "previous_state": self.history[-1]["state"] if self.history else "OPEN"
        })

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.history