from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.utils import calculate_risk_score, get_detector_coverage

router = APIRouter()

def get_db():
    db = SessionLocal(); yield db; db.close()

@router.get("/coverage")
def coverage():
    return get_detector_coverage()

@router.get("/status")
def status(db: Session = Depends(get_db)):
    return {"db":"connected","detectors":["COST_ANOMALY","DUPLICATE","TIMELINE","DATA_QUALITY"],"mode":"REAL_ESAKSHI","evidence_pipeline":"SCHEMA_READY","note":"Frontend/CV/integration missing"}
