"""
runs.py

Routes for logging runs and retrieving run history.
Handles post-run data entry and fetching past run logs.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional
from database import get_db
import models

router = APIRouter(prefix="/runs", tags=["Runs"])


class RunLogInput(BaseModel):
    date: date
    planned_distance_km: Optional[float] = None
    actual_distance_km: Optional[float] = None
    actual_time: Optional[str] = None
    feel_notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2026-03-01",
                "planned_distance_km": 10.0,
                "actual_distance_km": 10.5,
                "actual_time": "1:05:00",
                "feel_notes": "Felt strong today, knee was a little tight at km 8 but manageable",
            }
        }
    }


@router.post("/{user_id}")
def log_run(user_id: int, run_data: RunLogInput, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    run = models.RunLog(
        user_id=user_id,
        date=run_data.date,
        planned_distance_km=run_data.planned_distance_km,
        actual_distance_km=run_data.actual_distance_km,
        actual_time=run_data.actual_time,
        feel_notes=run_data.feel_notes,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return {"message": "Run logged successfully", "run_id": run.id}


@router.get("/{user_id}")
def get_run_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    runs = (
        db.query(models.RunLog)
        .filter(models.RunLog.user_id == user_id)
        .order_by(models.RunLog.date.desc())
        .all()
    )

    return {"user_id": user_id, "total_runs": len(runs), "runs": runs}
