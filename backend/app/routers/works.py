from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import List, Optional, Dict, Any
import math

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
        "source_work_id": w.source_work_id or w.work_id,
        "data_source": w.data_source,
        "mp_name": w.mp_name,
        "mp_type": w.mp_type,
        "constituency": w.constituency,
        "state": w.state,
        "district": w.district,
        "financial_year": w.financial_year,
        "sector": w.sector,
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
    """Full-dataset aggregations across all 60,362+ official records."""
    total_works = db.query(func.count(Work.work_id)).scalar() or 0
    total_recommended = db.query(func.coalesce(func.sum(Work.recommended_amount), 0.0)).scalar() or 0.0
    total_sanctioned = db.query(func.coalesce(func.sum(Work.sanctioned_amount), 0.0)).scalar() or 0.0
    total_expenditure = db.query(func.coalesce(func.sum(Work.actual_expenditure), 0.0)).scalar() or 0.0

    raw_status_rows = (
        db.query(
            Work.status,
            func.count(Work.work_id),
            func.coalesce(func.sum(Work.recommended_amount), 0.0),
            func.coalesce(func.sum(Work.sanctioned_amount), 0.0)
        )
        .group_by(Work.status)
        .all()
    )

    status_dict: Dict[str, Dict[str, Any]] = {}
    for st, count, rec, sanc in raw_status_rows:
        canonical = (st or "").strip()
        if not canonical:
            label = "Unspecified"
        elif canonical.upper() == "COMPLETED":
            label = "Completed"
        elif canonical.upper() == "ONGOING":
            label = "Ongoing"
        elif canonical.upper() == "SANCTIONED":
            label = "Sanctioned"
        elif canonical.upper() == "UNSANCTIONED":
            label = "Unsanctioned"
        else:
            label = canonical

        if label not in status_dict:
            status_dict[label] = {"status": label, "count": 0, "recommended_amount": 0.0, "sanctioned_amount": 0.0}
        status_dict[label]["count"] += count
        status_dict[label]["recommended_amount"] += float(rec or 0.0)
        status_dict[label]["sanctioned_amount"] += float(sanc or 0.0)

    by_status = sorted(status_dict.values(), key=lambda x: x["count"], reverse=True)

    state_rows = (
        db.query(
            Work.state,
            func.count(Work.work_id),
            func.coalesce(func.sum(Work.recommended_amount), 0.0),
            func.coalesce(func.sum(Work.sanctioned_amount), 0.0),
        )
        .group_by(Work.state)
        .order_by(func.coalesce(func.sum(Work.recommended_amount), 0.0).desc())
        .limit(15)
        .all()
    )
    by_state = [
        {
            "state": state or "Unspecified",
            "count": count,
            "recommended_amount": float(recommended or 0),
            "sanctioned_amount": float(sanctioned or 0),
            "sanction_rate": round((float(sanctioned or 0) / float(recommended or 1)) * 100, 1) if recommended else 0.0
        }
        for state, count, recommended, sanctioned in state_rows
    ]

    top_mp_rows = (
        db.query(
            Work.mp_name,
            Work.constituency,
            Work.state,
            func.count(Work.work_id),
            func.coalesce(func.sum(Work.recommended_amount), 0.0),
            func.coalesce(func.sum(Work.sanctioned_amount), 0.0),
        )
        .filter(Work.mp_name.isnot(None), Work.mp_name != "")
        .group_by(Work.mp_name, Work.constituency, Work.state)
        .order_by(func.coalesce(func.sum(Work.recommended_amount), 0.0).desc())
        .limit(8)
        .all()
    )
    top_mps = [
        {
            "mp_name": r[0],
            "constituency": r[1] or "N/A",
            "state": r[2] or "N/A",
            "works_count": r[3],
            "recommended_amount": float(r[4] or 0),
            "sanctioned_amount": float(r[5] or 0),
        }
        for r in top_mp_rows
    ]

    completed_count = status_dict.get("Completed", {}).get("count", 0)
    ongoing_count = status_dict.get("Ongoing", {}).get("count", 0)
    sanctioned_count = status_dict.get("Sanctioned", {}).get("count", 0)
    unsanctioned_count = status_dict.get("Unsanctioned", {}).get("count", 0)

    high_value_count = db.query(func.count(Work.work_id)).filter(
        or_(Work.sanctioned_amount >= 2500000, Work.recommended_amount >= 2500000)
    ).scalar() or 0

    crore_plus_count = db.query(func.count(Work.work_id)).filter(
        or_(Work.sanctioned_amount >= 10000000, Work.recommended_amount >= 10000000)
    ).scalar() or 0

    sanction_rate = round((total_sanctioned / total_recommended * 100), 2) if total_recommended > 0 else 0.0

    return {
        "total_works": int(total_works),
        "total_recommended": float(total_recommended),
        "total_sanctioned": float(total_sanctioned),
        "total_expenditure": float(total_expenditure),
        "sanction_rate": sanction_rate,
        "completed_count": int(completed_count),
        "ongoing_count": int(ongoing_count),
        "sanctioned_count": int(sanctioned_count),
        "unsanctioned_count": int(unsanctioned_count),
        "high_value_count": int(high_value_count),
        "crore_plus_count": int(crore_plus_count),
        "by_status": by_status,
        "by_state": by_state,
        "top_mps": top_mps,
        "source": "OFFICIAL_MPLADS_CSV",
    }


@router.get("/filters")
def works_filters(db: Session = Depends(get_db)):
    """Provides distinct filter choices from the official database."""
    states = [
        r[0] for r in db.query(Work.state)
        .distinct()
        .filter(Work.state.isnot(None), Work.state != "")
        .order_by(Work.state)
        .all()
    ]
    statuses = [
        r[0] for r in db.query(Work.status)
        .distinct()
        .filter(Work.status.isnot(None), Work.status != "")
        .order_by(Work.status)
        .all()
    ]
    years = [
        r[0] for r in db.query(Work.financial_year)
        .distinct()
        .filter(Work.financial_year.isnot(None), Work.financial_year != "")
        .order_by(desc(Work.financial_year))
        .all()
    ]
    return {
        "states": states,
        "statuses": statuses,
        "financial_years": years,
    }


@router.get("/")
def read_works(
    page: int = Query(1, ge=1),
    skip: Optional[int] = None,
    limit: int = Query(20, ge=1, le=1000),
    search: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    financial_year: Optional[str] = None,
    min_amount: Optional[float] = None,
    sort_by: Optional[str] = "sanctioned_amount",
    sort_order: Optional[str] = "desc",
    envelope: bool = Query(True),
    db: Session = Depends(get_db)
):
    query = db.query(Work)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Work.work_id.ilike(term),
                Work.work_description.ilike(term),
                Work.mp_name.ilike(term),
                Work.constituency.ilike(term),
                Work.state.ilike(term),
                Work.district.ilike(term),
                Work.implementing_agency.ilike(term),
            )
        )

    if state and state.upper() != "ALL":
        query = query.filter(Work.state == state)

    if status and status.upper() != "ALL":
        query = query.filter(Work.status.ilike(status))

    if financial_year and financial_year.upper() != "ALL":
        query = query.filter(Work.financial_year == financial_year)

    if min_amount is not None and min_amount > 0:
        query = query.filter(
            or_(
                Work.sanctioned_amount >= min_amount,
                Work.recommended_amount >= min_amount,
            )
        )

    total = query.count()

    sort_column_map = {
        "sanctioned_amount": Work.sanctioned_amount,
        "recommended_amount": Work.recommended_amount,
        "recommendation_date": Work.recommendation_date,
        "mp_name": Work.mp_name,
        "state": Work.state,
        "status": Work.status,
        "work_id": Work.work_id,
    }
    col = sort_column_map.get(sort_by, Work.sanctioned_amount)
    order_func = asc if (sort_order and sort_order.lower() == "asc") else desc
    query = query.order_by(order_func(col).nulls_last())

    offset = skip if skip is not None else (page - 1) * limit
    works = query.offset(offset).limit(limit).all()

    serialized = [serialize_work(w) for w in works]

    if not envelope:
        return serialized

    total_pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
    current_page = (offset // limit) + 1 if limit > 0 else 1

    return {
        "total": total,
        "page": current_page,
        "limit": limit,
        "total_pages": total_pages,
        "items": serialized,
    }


@router.get("/{work_id}", response_model=dict)
def read_work(work_id: str, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return serialize_work(work)
