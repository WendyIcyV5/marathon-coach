"""
gemini.py

Handles all interactions with the Google Gemini API.
Includes functions for generating training plans and analyzing run logs.
"""

from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_training_plan(user_data: dict) -> str:
    prompt = f"""
    You are an expert marathon coach. Generate a detailed week-by-week {user_data['race_type']} training plan in JSON format.

    Runner profile:
    - Name: {user_data['name']}
    - Race type: {user_data['race_type']}
    - Marathon date: {user_data['marathon_date']}
    - Goal finish time: {user_data['goal_time'] or 'not specified'}
    - Days available per week: {user_data['weekly_availability']}
    - Past races: {user_data['past_races']}

    Return a JSON object with this structure:
    {{
        "weeks": [
            {{
                "week_number": 1,
                "focus": "Base building",
                "runs": [
                    {{
                        "day": "Monday",
                        "type": "Easy run",
                        "distance_km": 8,
                        "notes": "Keep heart rate low"
                    }}
                ]
            }}
        ],
        "predicted_finish_time": "4:30:00",
        "advice": "Overall coaching advice here"
    }}

    Only return the JSON, no extra text.
    """
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text