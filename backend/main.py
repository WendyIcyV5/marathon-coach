"""
main.py

Entry point for the Marathon Coach FastAPI application.
Initializes the app, registers middleware, and includes all route modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import user, plan


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marathon Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(plan.router)

@app.get("/")
def root():
    return {"message": "Marathon Coach API is running"}
