"""
plan.py

Routes for generating and retrieving training plans.
Uses Gemini AI to create personalized marathon training plans.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import json
from services.gemini import generate_training_plan

router = APIRouter(prefix="/plan", tags=["Plan"])


@router.post("/{user_id}")
def create_plan(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    past_races = (
        db.query(models.PastRace).filter(models.PastRace.user_id == user_id).all()
    )

    user_data = {
        "name": user.name,
        "marathon_date": str(user.marathon_date),
        "goal_time": user.goal_time,
        "weekly_availability": user.weekly_availability,
        "race_type": user.race_type or "half_marathon",
        "past_races": [
            {
                "distance_km": r.distance_km,
                "finish_time": r.finish_time,
                "race_date": str(r.race_date) if r.race_date else None,
            }
            for r in past_races
        ],
    }

    plan_text = generate_training_plan(user_data)

    # clean up markdown code blocks if Gemini returns them
    clean_plan = (
        plan_text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    latest_plan = (
        db.query(models.TrainingPlan)
        .filter(models.TrainingPlan.user_id == user_id)
        .order_by(models.TrainingPlan.version.desc())
        .first()
    )

    version = (latest_plan.version + 1) if latest_plan else 1

    plan = models.TrainingPlan(user_id=user_id, plan_json=clean_plan, version=version)
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        "message": "Training plan generated",
        "plan_id": plan.id,
        "version": plan.version,
        "plan": json.loads(clean_plan),
    }


@router.get("/{user_id}")
def get_latest_plan(user_id: int, db: Session = Depends(get_db)):
    plan = (
        db.query(models.TrainingPlan)
        .filter(models.TrainingPlan.user_id == user_id)
        .order_by(models.TrainingPlan.version.desc())
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="No plan found for this user")

    return {
        "plan_id": plan.id,
        "version": plan.version,
        "generated_at": plan.generated_at,
        "plan": json.loads(plan.plan_json),
    }
