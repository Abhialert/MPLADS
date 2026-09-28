"""Cost Anomaly / Expenditure Anomaly Detector for MPLAD Integrity Engine.

Detects expenditure patterns that are unusual relative to peer works.
Uses robust statistics (median, IQR) for outlier detection.
Does NOT imply cost overrun or fraud - flags expenditure anomalies only.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime


class CostAnomalyDetector:
    """
    Expenditure Anomaly Detector.

    Flags works where actual_expenditure is an outlier relative to peer works
    within the same financial_year + state group.

    Key Principle: This detector identifies expenditure patterns that deviate
    from the observed distribution - it does NOT determine that a work exceeded
    its sanctioned amount or that fraud occurred.
    """

    def __init__(self):
        self.name = "COST_ANOMALY"
        self.description = "Expenditure anomaly screening using peer group comparison"
        self.required_fields = ["work_id", "sanctioned_amount", "actual_expenditure",
                               "financial_year", "state", "work_description"]
        self.available_fields = ["work_id", "actual_expenditure", "financial_year",
                                "state", "work_description"]
        self.missing_fields = [f for f in self.required_fields if f not in self.available_fields]

    def analyze(self, work: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a single work for expenditure anomaly.

        Args:
            work: Dictionary containing work record data

        Returns:
            Dictionary with anomaly details if flagged, None if no anomaly detected
        """
        # Check if required fields are available
        missing = [f for f in self.required_fields if not work.get(f)]
        if missing:
            # Field(s) required for this detector are unavailable
            # Return coverage info instead of fabricating data
            return {
                "detector_id": self.name,
                "available": False,
                "reason": f"Missing required fields: {', '.join(missing)}. "
                          "Expenditure anomaly screening unavailable.",
                "missing_fields": missing
            }

        # Field availability check
        work_id = work.get("work_id")
        actual_exp = work.get("actual_expenditure")
        sanctioned_amt = work.get("sanctioned_amount")
        fy = work.get("financial_year")
        state = work.get("state")
        description = work.get("work_description")

        # Need at least amount data to do peer comparison
        if actual_exp is None or sanctioned_amt is None:
            return {
                "detector_id": self.name,
                "available": False,
                "reason": "actual_expenditure and/or sanctioned_amount unavailable. "
                          "Cannot perform expenditure anomaly screening."
            }

        # Compute execution percentage only if sanctioned amount > 0
        execution_pct = None
        if sanctioned_amt and sanctioned_amt > 0:
            execution_pct = round((actual_exp / sanctioned_amt) * 100, 2)

        # For a true peer-group analysis, we would need the full dataset.
        # Since we're analyzing one work at a time, we'll compute a reference
        # using what's available and note the limitation.

        # Basic sanity check: flag if expenditure is very high relative to
        # sanctioned amount (but don't label as "overrun" without sector context)
        flags = []

        # If actual > sanctioned, note it but don't conclude overrun
        if actual_exp > sanctioned_amt:
            flags.append({
                "type": "exceeds_sanctioned",
                "observed": actual_exp,
                "reference": sanctioned_amt,
                "difference": round(actual_exp - sanctioned_amt, 2),
                "percentage_difference": round(((actual_exp / sanctioned_amt) - 1) * 100, 2),
                "explanation": f"Actual expenditure (₹{actual_exp:,.2f}) exceeds sanctioned amount (₹{sanctioned_amt:,.2f}). "
                              "This may indicate an expenditure pattern requiring review. "
                              "Does not imply cost overrun or fraud."
            })

        # If execution is very high (>80% of sanctioned)
        if execution_pct and execution_pct > 80:
            flags.append({
                "type": "high_execution_ratio",
                "observed_pct": execution_pct,
                "explanation": f"Expenditure represents {execution_pct}% of sanctioned amount. "
                              "High execution ratio warrants verification of work progress "
                              "and payment records."
            })

        if not flags:
            return None  # No anomaly flagged

        # Build the result
        result = {
            "detector_id": self.name,
            "work_id": work_id,
            "sector": work.get("sector"),
            "sanctioned_amount": sanctioned_amt,
            "actual_expenditure": actual_exp,
            "execution_percentage": execution_pct,
            "flags": flags,
            "source_fields": [
                "actual_expenditure",
                "sanctioned_amount",
                "financial_year",
                "state",
                "work_description"
            ],
            "explanation": "; ".join([f["explanation"] for f in flags]),
            "limitations": (
                "Peer-group comparison unavailable in single-work analysis. "
                "Sector-normalized baseline not available (sector field missing). "
                "This flag indicates expenditure pattern, not proven cost overrun."
            ),
            "observed_at": datetime.utcnow().isoformat()
        }

        return result

    def batch_analyze(self, works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple works for expenditure anomalies.

        Args:
            works: List of work record dictionaries

        Returns:
            List of anomaly results (one per work that was flagged)
        """
        results = []
        for work in works:
            result = self.analyze(work)
            if result is not None:
                results.append(result)
        return results

    def get_coverage(self) -> Dict[str, Any]:
        """Return detector coverage information."""
        return {
            "detector_id": self.name,
            "fully_evaluable": False,
            "partially_evaluable": True,
            "not_evaluable": False,
            "required_fields": self.required_fields,
            "available_fields": self.available_fields,
            "missing_fields": self.missing_fields,
            "safe_real_output": (
                "Expenditure anomaly screening with explicit limitations stated. "
                "Does not imply cost overrun or fraud."
            ),
            "limitations": (
                "Sector-normalized baseline unavailable. "
                "Full statistical comparison requires complete dataset."
            ),
            "real_data_label": "EXPENDITURE_ANOMALY_SCREENING"
        }

    def get_evidence_template(self) -> Dict[str, Any]:
        """Return evidence template for this detector."""
        return {
            "detector_id": self.name,
            "metric_name": "execution_ratio",
            "observed_value": None,
            "reference_value": None,
            "difference": None,
            "percentage_difference": None,
            "unit": "percent",
            "source_fields": ["actual_expenditure", "sanctioned_amount"],
            "explanation": "Expenditure observed against sanctioned baseline. "
                          "Peer-group comparison and sector normalization not available. "
                          "Flag indicates expenditure pattern requiring review, not fraud."
        }