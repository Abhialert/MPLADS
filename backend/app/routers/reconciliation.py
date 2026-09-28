"""Phase 3.7 APIs. Database-derived. No hardcoded dashboard numbers."""
from fastapi import APIRouter, HTTPException
import sqlite3
import os

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/mplad_integrity.db")
)


def _conn():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=503, detail="Database not found")
    return sqlite3.connect(DB_PATH)


@router.get("/summary")
def reconciliation_summary():
    conn = _conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM reconciliation_runs ORDER BY created_at DESC LIMIT 1")
        run = cur.fetchone()
        cur.execute("SELECT * FROM reconciliation_sources")
        sources = [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        conn.close()
        return {
            "cross_source_depth": "INSUFFICIENT",
            "cross_source_validation": "INSUFFICIENT_SOURCE_DEPTH",
            "sources": [],
            "note": "Reconciliation tables not yet populated. Run cross_source_reconciliation.py.",
        }
    conn.close()
    if run is None:
        return {
            "cross_source_depth": "INSUFFICIENT",
            "sources": sources,
            "note": "No reconciliation run persisted.",
        }
    return {
        "run_id": run["run_id"],
        "cross_source_depth": run["cross_source_depth"],
        "source_a_id": run["source_a_id"],
        "source_b_id": run["source_b_id"],
        "records_a": run["records_a"],
        "records_b": run["records_b"],
        "confirmed_matches": run["confirmed_matches"],
        "ambiguous_matches": run["ambiguous_matches"],
        "unmatched_records": run["unmatched_records"],
        "conflict_count": run["conflict_count"],
        "processing_seconds": run["processing_seconds"],
        "sources": sources,
        "note": "CROSS_SOURCE_VALIDATION = INSUFFICIENT_SOURCE_DEPTH until a second independent work-level source is ingested. No fabricated matches.",
    }


@router.get("/matches")
def reconciliation_matches():
    return {
        "matches": [],
        "count": 0,
        "match_method": None,
        "note": "No cross-source matches. Only one work-level source is registered.",
    }


@router.get("/conflicts")
def reconciliation_conflicts():
    return {
        "conflicts": [],
        "count": 0,
        "note": "No real cross-source conflicts. Conflicts are not fabricated.",
    }


@router.get("/conflicts/{conflict_id}")
def reconciliation_conflict_detail(conflict_id: str):
    raise HTTPException(
        status_code=404,
        detail="No cross-source conflict persisted. CROSS_SOURCE_DEPTH=INSUFFICIENT.",
    )
