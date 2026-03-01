"""
coach.py

Routes for AI coaching features.
Handles run analysis, plan adaptation, what-if scenarios and reminders.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import models
import json
from services.gemini import analyze_run_and_adapt_plan
from services.elevenlabs import generate_voice
from fastapi.responses import FileResponse

router = APIRouter(prefix="/coach", tags=["Coach"])


class WhatIfInput(BaseModel):
    scenario: str

    model_config = {
        "json_schema_extra": {
            "example": {"scenario": "What if I skip my long run this weekend?"}
        }
    }


@router.post("/analyze/{user_id}")
def analyze_and_adapt(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_plan = (
        db.query(models.TrainingPlan)
        .filter(models.TrainingPlan.user_id == user_id)
        .order_by(models.TrainingPlan.version.desc())
        .first()
    )

    if not current_plan:
        raise HTTPException(status_code=404, detail="No training plan found")

    run_logs = (
        db.query(models.RunLog)
        .filter(models.RunLog.user_id == user_id)
        .order_by(models.RunLog.date.desc())
        .limit(10)
        .all()
    )

    if not run_logs:
        raise HTTPException(status_code=400, detail="No run logs found to analyze")

    user_data = {
        "name": user.name,
        "marathon_date": str(user.marathon_date),
        "goal_time": user.goal_time,
        "race_type": user.race_type or "half_marathon",
    }

    logs_data = [
        {
            "date": str(r.date),
            "planned_distance_km": r.planned_distance_km,
            "actual_distance_km": r.actual_distance_km,
            "actual_time": r.actual_time,
            "feel_notes": r.feel_notes,
        }
        for r in run_logs
    ]

    result_text = analyze_run_and_adapt_plan(
        user_data, logs_data, json.loads(current_plan.plan_json)
    )

    clean_result = (
        result_text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    result = json.loads(clean_result)

    # save feedback to the run log
    latest_run = run_logs[0]
    latest_run.gemini_feedback = result["feedback"]
    db.commit()

    # if plan changed, save new version
    if result.get("plan_changed") and result.get("updated_plan"):
        new_plan = models.TrainingPlan(
            user_id=user_id,
            plan_json=json.dumps(result["updated_plan"]),
            version=current_plan.version + 1,
        )
        db.add(new_plan)
        db.commit()

    return {
        "feedback": result["feedback"],
        "plan_changed": result.get("plan_changed", False),
        "predicted_finish_time": result.get("predicted_finish_time"),
        "updated_plan": result.get("updated_plan"),
    }


@router.get("/reminder/{user_id}")
def get_reminder(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_run = (
        db.query(models.RunLog)
        .filter(models.RunLog.user_id == user_id)
        .order_by(models.RunLog.date.desc())
        .first()
    )

    from datetime import date, timedelta

    today = date.today()

    if not latest_run:
        return {
            "reminder": True,
            "message": "You haven't logged any runs yet. Time to get started!",
        }

    days_since = (today - latest_run.date).days

    if days_since >= 3:
        return {
            "reminder": True,
            "days_since_last_run": days_since,
            "message": f"You haven't logged a run in {days_since} days. Don't let your training slip!",
        }

    return {
        "reminder": False,
        "days_since_last_run": days_since,
        "message": "You're staying consistent, keep it up!",
    }


@router.get("/voice/{user_id}")
def get_voice_briefing(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_run = (
        db.query(models.RunLog)
        .filter(models.RunLog.user_id == user_id)
        .order_by(models.RunLog.date.desc())
        .first()
    )

    current_plan = (
        db.query(models.TrainingPlan)
        .filter(models.TrainingPlan.user_id == user_id)
        .order_by(models.TrainingPlan.version.desc())
        .first()
    )

    if not current_plan:
        raise HTTPException(status_code=404, detail="No plan found")

    plan = json.loads(current_plan.plan_json)
    next_week = plan["weeks"][0] if plan["weeks"] else None

    if latest_run and latest_run.gemini_feedback:
        text = f"Hey {user.name}, here's your coaching update. {latest_run.gemini_feedback}"
    elif next_week:
        text = f"Hey {user.name}, welcome to your training plan. This week's focus is {next_week['focus']}. You have {len(next_week['runs'])} runs scheduled. Let's get to work!"
    else:
        text = f"Hey {user.name}, your training plan is ready. Let's get started!"

    audio_path = generate_voice(text, filename=f"user_{user_id}_briefing.mp3")

    return FileResponse(audio_path, media_type="audio/mpeg", filename="briefing.mp3")
