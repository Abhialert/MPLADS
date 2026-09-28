#!/usr/bin/env python
"""
Ingestion script for MPLAD Integrity Engine.
Loads a CSV/JSON file via EsakshiCSVAdapter and stores works in the database.
Usage:
    python ingest.py <path_to_file>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.esakshi_adapter import EsakshiCSVAdapter
from app.models.database import SessionLocal, engine
from app.models.works import Work, Base
from sqlalchemy.orm import Session

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <path_to_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    # Initialize database (create tables if not exist)
    Base.metadata.create_all(bind=engine)
    
    # Configure adapter
    config = {
        "file_path": file_path,
        "source_name": "Ingested Dataset",
        "source_type": "REAL_ESAKSHI",
        "source_url": "file://" + os.path.abspath(file_path)
    }
    adapter = EsakshiCSVAdapter(config)
    
    # Fetch and normalize records
    print(f"Loading data from {file_path}...")
    records = adapter.fetch_data()
    print(f"Loaded {len(records)} records.")
    
    # Validate records
    valid_records = [r for r in records if adapter.validate_record(r)]
    print(f"Valid records: {len(valid_records)}")
    
    # Insert works into database
    db: Session = SessionLocal()
    try:
        for record in valid_records:
            # Check if work already exists
            existing = db.query(Work).filter(Work.work_id == record["work_id"]).first()
            if existing:
                # Update existing record (optional)
                for key, value in record.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
            else:
                work = Work(**record)
                db.add(work)
        db.commit()
        print(f"Successfully inserted/updated {len(valid_records)} works in the database.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting records: {e}")
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
    finally:
        db.close()

if __name__ == "__main__":
    main()
