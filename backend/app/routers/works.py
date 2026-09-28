from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.models.database import SessionLocal
from app.models.works import Work

router = APIRouter(
    prefix="/works",
    tags=["works"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_work(w: Work) -> dict:
    return {
        "work_id": w.work_id,
        "mp_name": w.mp_name,
        "constituency": w.constituency,
        "state": w.state,
        "district": w.district,
        "financial_year": w.financial_year,
        "work_description": w.work_description,
        "implementing_agency": w.implementing_agency,
        "contractor_name": w.contractor_name,
        "location_text": w.location_text,
        "latitude": w.latitude,
        "longitude": w.longitude,
        "is_within_constituency": w.is_within_constituency,
        "is_sc_area": w.is_sc_area,
        "is_st_area": w.is_st_area,
        "beneficiary_type": w.beneficiary_type,
        "asset_owner_type": w.asset_owner_type,
        "recommended_amount": w.recommended_amount,
        "sanctioned_amount": w.sanctioned_amount,
        "actual_expenditure": w.actual_expenditure,
        "total_paid": w.total_paid,
        "recommendation_date": w.recommendation_date.isoformat() if w.recommendation_date else None,
        "sanction_date": w.sanction_date.isoformat() if w.sanction_date else None,
        "ia_assignment_date": w.ia_assignment_date.isoformat() if w.ia_assignment_date else None,
        "expected_completion_date": w.expected_completion_date.isoformat() if w.expected_completion_date else None,
        "actual_completion_date": w.actual_completion_date.isoformat() if w.actual_completion_date else None,
        "final_payment_date": w.final_payment_date.isoformat() if w.final_payment_date else None,
        "marked_complete_date": w.marked_complete_date.isoformat() if w.marked_complete_date else None,
        "status": w.status,
        "source_url": w.source_url,
        "source_last_updated": w.source_last_updated.isoformat() if w.source_last_updated else None,
    }


@router.get("/summary")
def works_summary(db: Session = Depends(get_db)):
    """Aggregates over the full works table — not a page sample."""
    total_works = db.query(func.count(Work.work_id)).scalar() or 0
    total_recommended = db.query(func.coalesce(func.sum(Work.recommended_amount), 0.0)).scalar() or 0.0
    total_sanctioned = db.query(func.coalesce(func.sum(Work.sanctioned_amount), 0.0)).scalar() or 0.0
    total_expenditure = db.query(func.coalesce(func.sum(Work.actual_expenditure), 0.0)).scalar() or 0.0

    status_rows = (
        db.query(Work.status, func.count(Work.work_id), func.coalesce(func.sum(Work.recommended_amount), 0.0))
        .group_by(Work.status)
        .all()
    )
    by_status = [
        {"status": status or "Not publicly observed", "count": count, "recommended_amount": float(amount or 0)}
        for status, count, amount in status_rows
    ]

    state_rows = (
        db.query(
            Work.state,
            func.count(Work.work_id),
            func.coalesce(func.sum(Work.recommended_amount), 0.0),
            func.coalesce(func.sum(Work.sanctioned_amount), 0.0),
        )
        .group_by(Work.state)
        .order_by(func.count(Work.work_id).desc())
        .limit(12)
        .all()
    )
    by_state = [
        {
            "state": state or "Unspecified",
            "count": count,
            "recommended_amount": float(recommended or 0),
            "sanctioned_amount": float(sanctioned or 0),
        }
        for state, count, recommended, sanctioned in state_rows
    ]

    return {
        "total_works": int(total_works),
        "total_recommended": float(total_recommended),
        "total_sanctioned": float(total_sanctioned),
        "total_expenditure": float(total_expenditure),
        "by_status": by_status,
        "by_state": by_state,
        "source": "OFFICIAL_MPLADS_CSV",
    }


@router.get("/", response_model=List[dict])
def read_works(
    skip: int = 0,
    limit: int = Query(100, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    works = db.query(Work).offset(skip).limit(limit).all()
    return [serialize_work(w) for w in works]

@router.get("/{work_id}", response_model=dict)
def read_work(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return serialize_work(work)