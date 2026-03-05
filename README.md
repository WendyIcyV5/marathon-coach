# PaceIQ 🏃
### An AI running coach that listens, learns, and talks back.
![Pace IQ](image/2026-03-01_112345.png)

## What it does
PaceIQ generates a personalized marathon/half-marathon training plan and 
adapts it in real-time based on how your training is actually going — 
using natural language, not forms.

## Features
- AI-generated training plan tailored to your race date and goals
- Log runs in natural language — tell your coach how it went
- Plan automatically adapts based on your performance and feedback
- Voice coaching briefings powered by ElevenLabs
- Readiness reminders so you never fall behind

## Tech Stack
- **Backend:** Python, FastAPI, SQLite
- **AI:** Google Gemini 2.5
- **Voice:** ElevenLabs
- **Deployment:** Vultr

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Add `.env` with `GEMINI_API_KEY` and `ELEVENLABS_API_KEY`
4. `cd backend && py -m uvicorn main:app --reload`
5. Open `frontend/index.html` with Live Server