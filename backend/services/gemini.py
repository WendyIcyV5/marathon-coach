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
    print("generate_training_plan called with:", user_data)
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

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        print("Gemini response:", response)
        print("Gemini text:", response.text)
        return response.text
    except Exception as e:
        print("Gemini error:", str(e))
        raise e


def analyze_run_and_adapt_plan(
    user_data: dict, run_logs: list, current_plan: dict
) -> str:
    prompt = f"""
    You are an expert marathon coach analyzing a runner's recent training.

    Runner profile:
    - Name: {user_data['name']}
    - Race type: {user_data['race_type']}
    - Race date: {user_data['marathon_date']}
    - Goal time: {user_data['goal_time'] or 'not specified'}

    Current training plan:
    {current_plan}

    Recent run logs:
    {run_logs}

    Based on the run logs, provide:
    1. Feedback on recent performance
    2. Whether the current plan needs adjusting
    3. An updated plan if needed (same JSON structure as the current plan)

    Return a JSON object with this structure:
    {{
        "feedback": "Personalized coaching feedback here",
        "plan_changed": true or false,
        "updated_plan": {{ same structure as current plan, or null if no changes needed }},
        "predicted_finish_time": "updated prediction or same as before"
    }}

    Only return the JSON, no extra text.
    """
    response = client.models.generate_content(
        model="models/gemini-2.5-flash", contents=prompt
    )
    print("Gemini response:", response)
    print("Gemini text:", response.text)
    return response.text
