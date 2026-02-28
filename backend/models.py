"""
models.py

Defines all SQLAlchemy database models for the Marathon Coach app.
Tables: User, PastRace, TrainingPlan, RunLog.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    marathon_date = Column(Date, nullable=False)
    goal_time = Column(String, nullable=True)
    weekly_availability = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    race_type = Column(String, default="half_marathon")

    past_races = relationship("PastRace", back_populates="user")
    training_plans = relationship("TrainingPlan", back_populates="user")
    run_logs = relationship("RunLog", back_populates="user")


class PastRace(Base):
    __tablename__ = "past_races"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    finish_time = Column(String, nullable=False)
    race_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="past_races")


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    plan_json = Column(Text, nullable=False)
    version = Column(Integer, default=1)

    user = relationship("User", back_populates="training_plans")


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    planned_distance_km = Column(Float, nullable=True)
    actual_distance_km = Column(Float, nullable=True)
    actual_time = Column(String, nullable=True)
    feel_notes = Column(Text, nullable=True)
    gemini_feedback = Column(Text, nullable=True)

    user = relationship("User", back_populates="run_logs")
