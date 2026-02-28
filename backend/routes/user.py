"""
user.py

Routes for user onboarding.
Handles creating a new user profile and retrieving user info.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from database import get_db
import models

router = APIRouter(prefix="/user", tags=["User"])


class PastRaceInput(BaseModel):
    distance_km: float
    finish_time: str
    race_date: Optional[date] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "distance_km": 21.1,
                "finish_time": "2:15:00",
                "race_date": "2025-10-01"
            }
        }
    }

class UserCreate(BaseModel):
    name: str
    marathon_date: date
    goal_time: Optional[str] = None
    weekly_availability: int
    race_type: Optional[str] = "half_marathon"
    past_races: Optional[List[PastRaceInput]] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Wendy",
                "marathon_date": "2026-06-01",
                "goal_time": "2:00:00",
                "weekly_availability": 4,
                "race_type": "half_marathon",
                "past_races": [
                    {
                        "distance_km": 21.1,
                        "finish_time": "2:15:00",
                        "race_date": "2025-10-01"
                    }
                ]
            }
        }
    }


@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = models.User(
        name=user_data.name,
        marathon_date=user_data.marathon_date,
        goal_time=user_data.goal_time,
        weekly_availability=user_data.weekly_availability,
        race_type=user_data.race_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    for race in user_data.past_races:
        past_race = models.PastRace(
            user_id=user.id,
            distance_km=race.distance_km,
            finish_time=race.finish_time,
            race_date=race.race_date,
        )
        db.add(past_race)

    db.commit()
    return {"message": "User created successfully", "user_id": user.id}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
