"""Data Quality Detector for MPLAD Integrity Engine.

Detects inconsistencies and data quality issues in real data records.
These are DATA QUALITY FLAGS, not fraud indicators.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class DataQualityDetector:
    """Data Quality / Consistency Detector."""

    def __init__(self):
        self.name = "DATA_QUALITY"
        self.description = "Data quality and consistency flags for source data"
        self.required_fields = ["work_id"]

    def analyze(self, work: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a single work for data quality issues.

        Args:
            work: Dictionary containing work record data

        Returns:
            List of data quality issue dictionaries (may be empty if no issues)
        """
        issues = []
        work_id = work.get("work_id", "UNKNOWN")

        # MISSING_WORK_ID
        if not work.get("work_id") or work.get("work_id") == "":
            issues.append({
                "detector_id": self.name,
                "work_id": work.get("work_id") or "MISSING",
                "issue_type": "MISSING_WORK_ID",
                "severity": "HIGH",
                "field": "work_id",
                "observed_value": work.get("work_id"),
                "description": "Work ID is missing or empty.",
                "data_source": work.get("data_source", "REAL_ESAKSHI"),
                "created_at": datetime.utcnow().isoformat()
            })

        # ZERO_OR_NEGATIVE_RECOMMENDATION
        rec_amm = work.get("recommended_amount")
        if isinstance(rec_amm, (int, float)) and rec_amm is not None:
            if rec_amm < 0:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "NEGATIVE_RECOMMENDATION",
                    "severity": "HIGH",
                    "field": "recommended_amount",
                    "observed_value": rec_amm,
                    "description": f"Recommended amount is negative: ₹{rec_amm:,.2f}. "
                                  "This indicates a data entry error or source data issue.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })
            elif rec_amm == 0:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "ZERO_RECOMMENDATION",
                    "severity": "MEDIUM",
                    "field": "recommended_amount",
                    "observed_value": 0,
                    "description": "Recommended amount is zero. Verify if this represents "
                                  "a genuine zero-value recommendation or a data entry issue.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # ZERO_OR_NEGATIVE_SANCTION
        sanc_amm = work.get("sanctioned_amount")
        if isinstance(sanc_amm, (int, float)) and sanc_amm is not None:
            if sanc_amm < 0:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "NEGATIVE_SANCTION",
                    "severity": "HIGH",
                    "field": "sanctioned_amount",
                    "observed_value": sanc_amm,
                    "description": f"Sanctioned amount is negative: ₹{sanc_amm:,.2f}.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })
            elif sanc_amm == 0:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "ZERO_SANCTION",
                    "severity": "MEDIUM",
                    "field": "sanctioned_amount",
                    "observed_value": 0,
                    "description": "Sanctioned amount is zero. Verify source record.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # NEGATIVE_EXPENDITURE
        act_exp = work.get("actual_expenditure")
        if isinstance(act_exp, (int, float)) and act_exp is not None:
            if act_exp < 0:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "NEGATIVE_EXPENDITURE",
                    "severity": "HIGH",
                    "field": "actual_expenditure",
                    "observed_value": act_exp,
                    "description": f"Actual expenditure is negative: ₹{act_exp:,.2f}.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # EXPENDITURE_EXCEEDS_SANCTION
        if isinstance(sanc_amm, (int, float)) and isinstance(act_exp, (int, float)):
            if sanc_amm > 0 and act_exp > sanc_amm:
                # Note: this is a data quality flag, not a fraud indicator
                # Negative remaining amount is a data quality observation
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "EXPENDITURE_EXCEEDS_SANCTION",
                    "severity": "MEDIUM",
                    "field": "actual_expenditure",
                    "observed_value": f"₹{act_exp:,.2f} (sanctioned: ₹{sanc_amm:,.2f})",
                    "description": (f"Actual expenditure (₹{act_exp:,.2f}) exceeds sanctioned amount (₹{sanc_amm:,.2f}). "
                                  "This indicates a data inconsistency requiring review. "
                                  "Does not confirm fraud or cost overrun. The derived remaining amount is negative, "
                                  "which is a data-quality observation, not an error to suppress."),
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # DATE_ORDER_CONTRADICTION: Completion before sanction
        sanc_dt = work.get("sanction_date")
        comp_dt = work.get("actual_completion_date")
        if sanc_dt and comp_dt and isinstance(sanc_dt, datetime) and isinstance(comp_dt, datetime):
            if comp_dt < sanc_dt:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "COMPLETION_BEFORE_SANCTION",
                    "severity": "HIGH",
                    "field": "actual_completion_date / sanction_date",
                    "observed_value": f"Completion: {comp_dt.strftime('%Y-%m-%d')}, Sanction: {sanc_dt.strftime('%Y-%m-%d')}",
                    "description": "Actual completion date is earlier than sanction date. This is a data contradiction.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # SANCTION_BEFORE_RECOMMENDATION
        rec_dt = work.get("recommendation_date")
        if rec_dt and sanc_dt and isinstance(rec_dt, datetime) and isinstance(sanc_dt, datetime):
            if sanc_dt < rec_dt:
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "SANCTION_BEFORE_RECOMMENDATION",
                    "severity": "HIGH",
                    "field": "sanction_date / recommendation_date",
                    "observed_value": f"Sanction: {sanc_dt.strftime('%Y-%m-%d')}, Recommendation: {rec_dt.strftime('%Y-%m-%d')}",
                    "description": "Sanction date is earlier than recommendation date. This is a data contradiction.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # COMPLETED_WITHOUT_COMPLETION_DATE
        status = work.get("status")
        if status and isinstance(status, str):
            status_upper = status.strip().upper()
            if status_upper == "COMPLETED" and not work.get("actual_completion_date"):
                issues.append({
                    "detector_id": self.name,
                    "work_id": work_id,
                    "issue_type": "COMPLETED_WITHOUT_COMPLETION_DATE",
                    "severity": "MEDIUM",
                    "field": "status / actual_completion_date",
                    "observed_value": f"Status: {status}, Completion date: NULL",
                    "description": "Work marked as COMPLETED but no actual completion date recorded.",
                    "data_source": work.get("data_source", "REAL_ESAKSHI"),
                    "created_at": datetime.utcnow().isoformat()
                })

        # NON_COMPLETED_WITH_COMPLETION_DATE
        if work.get("actual_completion_date") and status_upper != "COMPLETED" and status_upper is not None:
            issues.append({
                "detector_id": self.name,
                "work_id": work_id,
                "issue_type": "NON_COMPLETED_WITH_COMPLETION_DATE",
                "severity": "MEDIUM",
                "field": "status / actual_completion_date",
                "observed_value": f"Status: {status}, Completion date: present",
                "description": "Actual completion date is recorded but work status is not COMPLETED.",
                "data_source": work.get("data_source", "REAL_ESAKSHI"),
                "created_at": datetime.utcnow().isoformat()
            })

        # STATUS_DATE_CONTRADICTION (basic check)
        if (work.get("actual_completion_date") and work.get("actual_expenditure") is not None
            and work.get("actual_expenditure") > 0):
            # If expenditure > 0 and status is RECOMMENDED (before sanction), check contradiction
            if status_upper == "RECOMMENDED" and (work.get("sanction_date") or work.get("actual_expenditure") > 0):
                # Only flag if both sanction and expenditure exist, indicating status may be outdated
                if work.get("sanction_date") and work.get("actual_expenditure", 0) > 0:
                    pass  # Not a contradiction per se; skip

        # MISSING_SANCTIONED_AMOUNT but expenditure > 0
        if work.get("actual_expenditure", 0) > 0 and not work.get("sanctioned_amount"):
            issues.append({
                "detector_id": self.name,
                "work_id": work_id,
                "issue_type": "EXPENDITURE_WITHOUT_SANCTIONED_AMOUNT",
                "severity": "MEDIUM",
                "field": "actual_expenditure / sanctioned_amount",
                "observed_value": f"Expenditure > 0, sanctioned_amount: NULL",
                "description": "Actual expenditure is positive but sanctioned amount is unavailable. "
                              "This affects derived calculations such as remaining amount and execution ratio.",
                "data_source": work.get("data_source", "REAL_ESAKSHI"),
                "created_at": datetime.utcnow().isoformat()
            })

        return issues

    def batch_analyze(self, works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple works for data quality issues."""
        results = []
        for work in works:
            issues = self.analyze(work)
            for issue in issues:
                results.append(issue)
        return results

    def get_coverage(self) -> Dict[str, Any]:
        """Return detector coverage."""
        return {
            "detector_id": self.name,
            "fully_evaluable": True,
            "partially_evaluable": False,
            "not_evaluable": False,
            "required_fields": self.required_fields,
            "available_fields": ["work_id", "recommended_amount", "sanctioned_amount",
                                "actual_expenditure", "recommendation_date", "sanction_date",
                                "actual_completion_date", "status", "data_source"],
            "missing_fields": [],
            "safe_real_output": "DATA_QUALITY_FLAG",
            "limitations": "Operates on available fields; some checks require both amount fields"
        }

    def get_evidence_template(self) -> Dict[str, Any]:
        """Return evidence template."""
        return {
            "detector_id": self.name,
            "metric_name": "data_quality_issue_type",
            "observed_value": None,
            "reference_value": None,
            "difference": None,
            "percentage_difference": None,
            "unit": "flag",
            "source_fields": ["work_id", "status", "recommended_amount",
                             "sanctioned_amount", "actual_expenditure",
                             "recommendation_date", "sanction_date", "actual_completion_date"],
            "explanation": "Data quality flag identifying inconsistencies or missing data. "
                          "Not an anomaly or fraud indicator."
        }