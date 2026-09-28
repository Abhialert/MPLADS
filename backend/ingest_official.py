#!/usr/bin/env python3
"""
Ingest official MPLADS CSV into the API database.
Usage:
    python ingest_official.py <path_to_csv>
"""
import sys
import os

# Ensure we can import from the backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.adapters.official_mplads_adapter import OfficialMPLADSFileAdapter
from app.models.database import SessionLocal, engine
from app.models.works import Work, Base
from sqlalchemy.orm import Session

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_official.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Initialize database (create tables if not exist)
    Base.metadata.create_all(bind=engine)

    # Configure adapter for official CSV
    config = {
        "file_path": file_path,
        "source_name": "MPLADS Official CSV Export",
        "source_type": "OFFICIAL_MPLADS_CSV",
        "source_url": "https://mplads.mospi.gov.in/digigov/dashboard.html"
    }
    adapter = OfficialMPLADSFileAdapter(config)

    # Fetch and normalize records
    print(f"Loading data from {file_path}...")
    records = adapter.fetch_data()
    print(f"Loaded {len(records)} records.")

    # Validate records
    valid_records = [r for r in records if adapter.validate_record(r)]
    print(f"Valid records: {len(valid_records)}")

    if not valid_records:
        print("No valid records to insert.")
        return

    # Insert works into database
    db: Session = SessionLocal()
    try:
        inserted = 0
        updated = 0
        for record in valid_records:
            # Check if work already exists
            existing = db.query(Work).filter(Work.work_id == record["work_id"]).first()
            if existing:
                # Update existing record (optional)
                for key, value in record.items():
                    if hasattr(existing, key) and value is not None and key not in ['created_at']:
                        setattr(existing, key, value)
                # Always update the timestamp
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                work = Work(**record)
                db.add(work)
                inserted += 1
        db.commit()
        print(f"Successfully inserted {inserted} new works and updated {updated} existing works.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting records: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

    # Show a sample
    db = SessionLocal()
    try:
        sample = db.query(Work).limit(5).all()
        print("\nSample works:")
        for w in sample:
            print(f"  {w.work_id}: {w.work_description[:50] if w.work_description else 'N/A'}")

        # Show total count
        total = db.query(Work).count()
        print(f"\nTotal works in database: {total}")
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    main()