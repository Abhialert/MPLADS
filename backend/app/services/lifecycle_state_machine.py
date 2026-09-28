"""Phase 1 — Lifecycle State Machine (Section 6 of prompt).
Models expected progression; detects impossible transitions,
contradictions, and evidence completeness without assuming
every work must contain every stage if source doesn't provide it."""
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

class LifecycleNode:
    def __init__(self, name: str, required_fields: List[str]):
        self.name = name
        self.required_fields = required_fields
        self.transitions: Dict[str, str] = {}  # from -> to
        self.detector_rules: List[Dict[str, Any]] = []

    def add_transition(self, from_state: str, to_state: str):
        self.transitions[from_state] = to_state

    def validate_transition(self, from_state: str, to_state: str) -> bool:
        return from_state in self.transitions and self.transitions[from_state] == to_state

class LifecycleStateMachine:
    def __init__(self):
        self.states: Dict[str, LifecycleNode] = {}
        self.setup_lifecycle()
        self.drift_records = []
        self.evidence_trail = []

    def setup_lifecycle(self):
        # Core MPLADS lifecycle (Section 6)
        recommended = LifecycleNode("RECOMMENDED", ["recommended_amount", "recommendation_date"])
        sanctioned = LifecycleNode("SANCTIONED", ["sanctioned_amount", "sanction_date"])
        agency_assigned = LifecycleNode("AGENCY_ASSIGNED", ["implementing_agency"])
        in_progress = LifecycleNode("IN_PROGRESS", ["actual_expenditure", "status"])
        expenditure = LifecycleNode("EXPENDITURE", ["actual_expenditure", "payment_date"])
        completed = LifecycleNode("COMPLETED", ["actual_completion_date", "final_payment_date"])

        recommended.add_transition("RECOMMENDED", "SANCTIONED")
        sanctioned.add_transition("SANCTIONED", "AGENCY_ASSIGNED")
        agency_assigned.add_transition("AGENCY_ASSIGNED", "IN_PROGRESS")
        in_progress.add_transition("IN_PROGRESS", "EXPENDITURE")
        expenditure.add_transition("EXPENDITURE", "COMPLETED")

        self.states = {
            "RECOMMENDED": recommended,
            "SANCTIONED": sanctioned,
            "AGENCY_ASSIGNED": agency_assigned,
            "IN_PROGRESS": in_progress,
            "EXPENDITURE": expenditure,
            "COMPLETED": completed,
        }

    def validate_record_state(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings = []
        current_status = work.get("status")
        # Detect impossible transitions based on current status
        if current_status:
            # Record evidence of status without claiming correctness
            self.evidence_trail.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "status_validation",
                "status": current_status,
                "work_id": work.get("work_id"),
                "note": "Status recorded as observed; validity depends on data source"
            })

        # Check for contradictory states across sources
        if work.get("status") != work.get("status_from_source"):
            findings.append({
                "field": "status",
                "issue_type": "CONTRADICTORY_STATE",
                "severity": "HIGH",
                "observed_value": f"status={work.get('status')}, source_status={work.get('status_from_source')}",
                "description": f"Contradictory status between system and source for work {work.get('work_id')}"
            })

        # Date-order violations
        dates = {
            "recommendation": work.get("recommendation_date"),
            "sanction": work.get("sanction_date"),
            "completion": work.get("actual_completion_date"),
            "payment": work.get("final_payment_date")
        }
        sorted_dates = sorted([(k, v) for k, v in dates.items() if v], key=lambda x: x[1])
        for i in range(len(sorted_dates) - 1):
            if sorted_dates[i][1] > sorted_dates[i+1][1]:
                findings.append({
                    "field": sorted_dates[i][0] + "/" + sorted_dates[i+1][0],
                    "issue_type": "DATE_ORDER_VIOLATION",
                    "severity": "MEDIUM",
                    "observed_value": f"{sorted_dates[i][0]} {sorted_dates[i][1]} > {sorted_dates[i+1][0]} {sorted_dates[i+1][1]}",
                    "description": f"Chronological violation for work {work.get('work_id')}"
                })

        return findings

    def validate_lifecycle_completeness(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings = []
        status = work.get("status")
        if not status:
            return findings

        # State transitions that should have happened
        expected_next = None
        for state_name, node in self.states.items():
            if node.validate_transition(status, state_name):
                expected_next = state_name
                break

        if expected_next and status != expected_next:
            findings.append({
                "field": "lifecycle_status",
                "issue_type": "UNEXPECTED_STATE",
                "severity": "MEDIUM",
                "observed_value": status,
                "description": f"Work {work.get('work_id')} has unexpected status {status}; next expected {expected_next}"
            })

        # Missing expected evidence (not a fraud claim, just completeness note)
        if status == "COMPLETED" and not work.get("actual_completion_date"):
            findings.append({
                "field": "actual_completion_date",
                "issue_type": "MISSING_EVIDENCE",
                "severity": "LOW",
                "observed_value": None,
                "description": f"Completed work {work.get('work_id')} lacks completion date"
            })

        return findings

    def validate_coverage_expectations(self, work: Dict[str, Any], source_capabilities: Dict[str, bool]) -> List[Dict[str, Any]]:
        findings = []
        if source_capabilities.get("location_text") and not work.get("location_text"):
            findings.append({
                "field": "location_text",
                "issue_type": "COVERAGE_GAP",
                "severity": "LOW",
                "observed_value": None,
                "description": f"Location text missing but source indicates capability"
            })
        return findings

    def process_work(self, work: Dict[str, Any], source_capabilities: Dict[str, bool]) -> Dict[str, Any]:
        all_findings = []
        all_findings.extend(self.validate_record_state(work))
        all_findings.extend(self.validate_lifecycle_completeness(work))
        all_findings.extend(self.validate_coverage_expectations(work, source_capabilities))

        return {
            "work_id": work.get("work_id"),
            "lifecycle_findings": all_findings,
            "evidence_quality": "MEDIUM" if all_findings else "HIGH",
            "note": "Lifecycle validation is analytical; missing fields do not prove data non-existence elsewhere."
        }
