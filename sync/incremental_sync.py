#!/usr/bin/env python3
"""Scheduled incremental sync skeleton.
Requires verified public endpoint to become operational.
Until then: manual CSV export from https://mplads.mospi.gov.in/digigov/dashboard.html
is the verified path, and CSV is fallback per your instruction.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.works import SourceRun

def sync_incremental():
    run = SourceRun(
        source_name="mplads_public",
        source_type="REAL_ESAKSHI",
        source_url="https://mplads.mospi.gov.in/digigov/dashboard.html",
        status="PENDING_VERIFICATION",
        retrieved_at=datetime.utcnow(),
        dataset_version="unverified"
    )
    db = SessionLocal()
    try:
        db.add(run)
        db.commit()
        print("SOURCE_RUN: Incremental sync scheduled but endpoint unverified.")
        print("ACTION NEEDED: Confirm public CSV/API endpoint or use manual CSV (fallback).")
    finally:
        db.close()

if __name__ == "__main__":
    sync_incremental()
