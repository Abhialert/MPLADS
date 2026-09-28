@echo off
REM Start MPLAD Integrity Engine backend (FastAPI + SQLite)
REM Uses existing init_db.py; DB: data/mplad_integrity.db
REM No synthetic data loaded into production DB automatically.
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
