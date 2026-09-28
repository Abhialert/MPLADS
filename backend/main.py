from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.routers import works
from app.routers import reconciliation
from app.models.database import SessionLocal, engine
from app.models.works import Work

app = FastAPI(
    title="MPLAD Integrity Engine",
    description="AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation",
    version="0.1.0"
)

# CORS middleware - restrict to specific origins for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:4173,http://127.0.0.1:4173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
from app.routers import reconciliation
app.include_router(works.router, prefix="/api")
app.include_router(reconciliation.router, prefix="/api")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        # Test database connection
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        print("[INFO] Database connection established")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        # Don't fail startup, but log the error

@app.get("/health")
async def health_check():
    """Health check endpoint with database verification"""
    try:
        # Test database connection
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_status = "CONNECTED"
    except Exception as e:
        db_status = f"DISCONNECTED: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "CONNECTED" else "degraded",
        "service": "MPLAD Integrity Engine Backend",
        "database": db_status
    }

@app.get("/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status with proper error handling"""
    try:
        total_works = db.query(func.count(Work.work_id)).scalar() or 0
        return {
            "db": f"CONNECTED ({os.getenv('DATABASE_URL', 'data/mplad_integrity.db')})",
            "db_status": "ONLINE",
            "total_works": total_works,
            "mode": "REAL_DATABASE_OBSERVATION",
            "evidence_pipeline": "ACTIVE_SCHEMA_READY",
            "detectors": [
                "CostAnomalyDetector",
                "TimelineAnomalyDetector",
                "PotentialDuplicateDetector",
                "DataQualityDetector",
                "GeographicComplianceDetector",
                "SCSTAllocationDetector"
            ],
            "note": "Production DB enforces strict provenance. Unobserved public fields remain NULL and are flagged with 'Not publicly observed' audit badges."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@app.get("/coverage")
async def get_detector_coverage(db: Session = Depends(get_db)):
    """Get detector coverage with proper error handling"""
    try:
        total_works = db.query(func.count(Work.work_id)).scalar() or 0
        return {
            "Cost Anomaly (Sanction vs Expenditure)": True,
            "Timeline Anomaly (Completion & Lags)": True,
            "Potential Duplicate Works": True,
            "Data Quality & Completeness Audit": True,
            "Geographic & Boundary Compliance": True,
            "SC/ST Reserved Quota Tracking": True,
            "Vendor & IA Concentration Analysis": False,
            "metadata": {
                "total_records_evaluated": total_works,
                "provenance_standard": "MOSPI / eSAKSHI Verified",
                "last_audit_run": "Live on request"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detector coverage: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve frontend or API info"""
    frontend_path = "app/index.html"
    if os.path.exists(frontend_path):
        with open(frontend_path) as f:
            return f.read()
    return """
    <h1>MPLAD Integrity Engine Backend API</h1>
    <p>API docs available at <a href='/docs'>/docs</a></p>
    <p><a href='/health'>Health Check</a></p>
    <p><a href='/status'>System Status</a></p>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
