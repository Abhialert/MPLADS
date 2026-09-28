"""Utility functions for MPLAD Integrity Engine."""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.database import SessionLocal


def get_db() -> Session:
    """Provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_source_availability() -> Dict[str, Any]:
    """Return which detectors are available given the source data."""
    return {
        "cost_anomaly": {"available": True, "mode": "PARTIALLY_EVALUABLE",
                         "reason": "Sector field not publicly available; peer-group screening only"},
        "duplicate": {"available": True, "mode": "PARTIALLY_EVALUABLE",
                      "reason": "Text/entity similarity only; no coordinates available"},
        "timeline": {"available": True, "mode": "PARTIALLY_EVALUABLE",
                     "reason": "Observed durations only; no guideline expectation comparison"},
        "guideline_compliance": {"available": False, "mode": "NOT_EVALUABLE",
                                 "reason": "Required beneficiary/area fields not publicly available"},
        "contractor_concentration": {"available": False, "mode": "NOT_EVALUABLE",
                                     "reason": "Contractor data not publicly available"},
        "payment_pattern": {"available": False, "mode": "NOT_EVALUABLE",
                            "reason": "Transaction-level payment data not publicly available"},
        "financial_physical_mismatch": {"available": False, "mode": "NOT_EVALUABLE",
                                        "reason": "Physical progress not publicly available"},
        "early_warning": {"available": True, "mode": "PARTIALLY_EVALUABLE",
                          "reason": "Status-based signals only; no physical progress"},
        "data_quality": {"available": True, "mode": "FULLY_EVALUABLE",
                         "reason": "All checks operate on available source fields"},
    }


def get_detection_weights() -> Dict[str, float]:
    """Return configurable detection weights for risk scoring."""
    return {
        "guideline_issue": 40,
        "expenditure_anomaly": 25,
        "potential_duplicate": 25,
        "timeline_anomaly": 20,
        "contractor_concentration": 15,
        "payment_pattern": 15,
        "financial_physical_mismatch": 20,
        "data_quality_flag": 5,
    }


def calculate_risk_score(evidence_list: List[Dict[str, Any]], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Calculate transparent review-risk score from evidence list.

    Each evidence item should contain detector_id and severity.
    Weights are configurable; default values are design weights, not empirical probabilities.
    """
    if weights is None:
        weights = get_detection_weights()

    score = 0.0
    contributions = {}

    for evidence in evidence_list:
        detector_id = evidence.get("detector_id")
        severity = evidence.get("severity", "LOW")

        weight = weights.get(detector_id, 10)

        if severity == "HIGH":
            contribution = weight
        elif severity == "MEDIUM":
            contribution = weight * 0.5
        else:
            contribution = weight * 0.25

        contributions[detector_id] = contributions.get(detector_id, 0) + contribution
        score += contribution

    # Determine risk level
    if score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": round(score, 2),
        "risk_level": risk_level,
        "contributions": contributions,
        "weights_used": weights,
        "methodology": "Transparent configurable weights; design values, not empirical probabilities",
        "calculated_at": datetime.utcnow().isoformat()
    }


def get_risk_summary(work_id: str, db_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate human-readable risk summary."""
    if not db_result:
        return {"work_id": work_id, "risk_level": "UNKNOWN", "reason": "No evidence available"}

    score = db_result.get("risk_score", 0)
    level = db_result.get("risk_level", "LOW")
    contributions = db_result.get("contributions", {})

    breakdown = []
    for detector, contrib in contributions.items():
        if contrib > 0:
            breakdown.append(f"{detector}: +{contrib}")

    total = sum(contributions.values())

    return {
        "work_id": work_id,
        "risk_score": score,
        "risk_level": level,
        "breakdown": breakdown,
        "total": round(total, 2),
        "note": "Risk score is review-priority indicator, not fraud probability"
    }


def get_source_coverage(source: str = "REAL_ESAKSHI") -> Dict[str, Any]:
    """Return source coverage information for a given source."""
    return {
        "source": source,
        "coverage": {
            "work_id": "PUBLIC_OBSERVED",
            "mp_name": "PUBLIC_OBSERVED",
            "constituency": "PUBLIC_OBSERVED",
            "state": "PUBLIC_OBSERVED",
            "financial_year": "PUBLIC_OBSERVED",
            "work_description": "PUBLIC_OBSERVED",
            "implementing_agency": "PUBLIC_OBSERVED",
            "location_text": "PUBLIC_OBSERVED",
            "recommended_amount": "PUBLIC_OBSERVED",
            "sanctioned_amount": "PUBLIC_OBSERVED",
            "actual_expenditure": "PUBLIC_OBSERVED",
            "recommendation_date": "PUBLIC_OBSERVED",
            "sanction_date": "PUBLIC_OBSERVED",
            "actual_completion_date": "PUBLIC_OBSERVED",
            "status": "PUBLIC_OBSERVED",
            "district": "NOT_PUBLICLY_OBSERVED",
            "sector": "NOT_PUBLICLY_OBSERVED",
            "contractor_name": "NOT_PUBLICLY_OBSERVED",
            "beneficiary_type": "NOT_PUBLICLY_OBSERVED",
            "asset_owner_type": "NOT_PUBLICLY_OBSERVED",
            "latitude": "NOT_PUBLICLY_OBSERVED",
            "longitude": "NOT_PUBLICLY_OBSERVED",
            "payment_transactions": "NOT_PUBLICLY_OBSERVED",
            "progress_history": "NOT_PUBLICLY_OBSERVED",
        }
    }


def get_detector_coverage() -> Dict[str, Any]:
    """Return coverage for all detectors."""
    return {
        "COST_ANOMALY": {
            "capability": "PARTIALLY_EVALUABLE",
            "real_mode_label": "EXPENDITURE_ANOMALY_SCREENING",
            "required": ["work_id", "sanctioned_amount", "actual_expenditure", "financial_year", "state"],
            "available": ["work_id", "actual_expenditure", "financial_year", "state"],
            "missing": ["sector"],
            "reason": "Sector field unavailable; peer-group screening without sector normalization"
        },
        "DUPLICATE": {
            "capability": "FULLY_EVALUABLE",
            "real_mode_label": "POTENTIAL_DUPLICATE",
            "required": ["work_id", "work_description", "location_text", "constituency", "state", "recommendation_date"],
            "available": ["work_id", "work_description", "location_text", "constituency", "state", "recommendation_date"],
            "missing": ["latitude", "longitude"],
            "reason": "Geographic distance unavailable; text/entity similarity only"
        },
        "TIMELINE": {
            "capability": "PARTIALLY_EVALUABLE",
            "real_mode_label": "OBSERVED_DURATION_ANALYSIS",
            "required": ["recommendation_date", "sanction_date", "actual_completion_date"],
            "available": ["recommendation_date", "sanction_date", "actual_completion_date"],
            "missing": ["ia_assignment_date", "expected_completion_date", "final_payment_date", "marked_complete_date"],
            "reason": "Only observed durations; no guideline expectation comparison"
        },
        "GUIDELINE_COMPLIANCE": {
            "capability": "NOT_EVALUABLE",
            "real_mode_label": "NOT_EVALUABLE",
            "required": ["beneficiary_type", "asset_owner_type", "is_sc_area", "is_st_area"],
            "available": [],
            "missing": ["beneficiary_type", "asset_owner_type", "is_sc_area", "is_st_area"],
            "reason": "Required fields not publicly available"
        },
        "CONTRACTOR_CONCENTRATION": {
            "capability": "NOT_EVALUABLE",
            "real_mode_label": "NOT_EVALUABLE",
            "required": ["contractor_name"],
            "available": [],
            "missing": ["contractor_name"],
            "reason": "Contractor data not publicly available"
        },
        "PAYMENT_PATTERN": {
            "capability": "NOT_EVALUABLE",
            "real_mode_label": "NOT_EVALUABLE",
            "required": ["payment_date", "amount"],
            "available": [],
            "missing": ["payment_date", "amount", "payment_stage", "payment_status"],
            "reason": "Transaction-level payment data not publicly available"
        },
        "FINANCIAL_PHYSICAL_MISMATCH": {
            "capability": "NOT_EVALUABLE",
            "real_mode_label": "NOT_EVALUABLE",
            "required": ["physical_progress_pct", "financial_progress_pct"],
            "available": ["financial_progress_pct (derived)"],
            "missing": ["physical_progress_pct"],
            "reason": "Physical progress not publicly available"
        },
        "EARLY_WARNING": {
            "capability": "PARTIALLY_EVALUABLE",
            "real_mode_label": "EARLY_WARNING_SIGNAL",
            "required": ["status", "sanctioned_amount", "actual_expenditure"],
            "available": ["status", "sanctioned_amount", "actual_expenditure"],
            "missing": ["physical_progress_pct"],
            "reason": "Status-based signals only; no physical progress"
        },
        "DATA_QUALITY": {
            "capability": "FULLY_EVALUABLE",
            "real_mode_label": "DATA_QUALITY_FLAG",
            "required": ["work_id", "status", "actual_expenditure", "sanctioned_amount"],
            "available": ["work_id", "status", "actual_expenditure", "sanctioned_amount"],
            "missing": [],
            "reason": "All checks operate on available source fields"
        }
    }