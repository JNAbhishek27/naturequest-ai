"""
AI Service module for NatureQuest AI.
Handles structured mission generation using open-weight Gemma models via Google Gen AI SDK
with graceful error handling, output validation, and fallback support.
"""

import os
import json
import re
from typing import Dict, Any, Tuple

# Configuration
GEMMA_MODEL_ID = os.getenv("GEMMA_MODEL_ID", "gemma-3-4b-it")
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

PROMPT_SYSTEM = (
    "You are NatureQuest AI, an outdoor discovery guide designed for the Hacktoberfest Touch Grass Challenge. "
    "Your mission is: 'A little less scrolling. A little more exploring.'\n"
    "Create a safe, engaging, age-inclusive, practical outdoor nature mission that encourages the user to put "
    "away their screens and observe real-world nature in their immediate surroundings (parks, gardens, neighborhood, campus, or trail).\n"
    "Crucial Guidelines:\n"
    "1. Every task must be actionable, achievable without purchasing equipment, and safe.\n"
    "2. It must be well-adapted to the specified environment, available time, and difficulty.\n"
    "3. Appropriate for global locations, including urban and suburban neighborhoods in India and worldwide.\n"
    "4. DO NOT invent precise user coordinates, live weather, or local species sightings.\n"
    "5. DO NOT claim to identify actual specific plants or animals in real time.\n"
    "6. Respond strictly with a single valid JSON object following the required schema."
)

JSON_SCHEMA_INSTRUCTION = """
You MUST return ONLY valid JSON matching this schema:
{
  "mission_title": "string (engaging, creative, outdoor-focused title)",
  "mission_description": "string (1-2 sentences setting the context for stepping outside)",
  "estimated_minutes": integer (10, 15, or 30),
  "three_to_five_tasks": [
    "string (task 1: clear sensory observation or discovery step)",
    "string (task 2: actionable outdoor activity)",
    "string (task 3: another observation or mindful inquiry)",
    "string (optional task 4)",
    "string (optional task 5)"
  ],
  "observation_tips": [
    "string (tip 1: e.g., how to notice textures, sounds, wind, or leaf patterns)",
    "string (tip 2)"
  ],
  "one_reflection_question": "string (a thoughtful question to ponder after heading back)",
  "safety_reminders": [
    "string (safety reminder 1: e.g., stay mindful of traffic/footing)",
    "string (safety reminder 2: e.g., do not ingest wild plants or disturb wildlife)"
  ],
  "low_screen_mode_instruction": "string (e.g., 'Review tasks now, silence notifications, keep your phone in your pocket, and look up!')"
}
"""


def is_model_configured() -> bool:
    """Check if the API key is set for live AI inference."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return bool(key and key.strip())


def get_model_status() -> Dict[str, Any]:
    """Return model status without exposing any credentials."""
    configured = is_model_configured()
    model_name = os.getenv("GEMMA_MODEL_ID", "gemma-3-4b-it")
    return {
        "configured": configured,
        "engine": "Gemma Open-Weight Model (Hosted Inference via Google Gen AI SDK)" if configured else "Sample Mission Engine (API Key Not Configured)",
        "model_id": model_name,
        "mode": "live_ai" if configured else "fallback_sample",
        "notice": "Gemma is an open-weights model family by Google. Hosted inference requires GEMINI_API_KEY or GOOGLE_API_KEY."
    }


def clean_json_text(text: str) -> str:
    """Extract and clean JSON substring from raw model output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Search for outer braces if still wrapped
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def validate_mission_schema(data: Any, expected_minutes: int = 15) -> Dict[str, Any]:
    """Validate that the generated data matches the required contract."""
    if not isinstance(data, dict):
        raise ValueError("Mission output is not a JSON object")

    title = str(data.get("mission_title", "")).strip()
    if not title:
        title = "Outdoor Discovery Expedition"

    desc = str(data.get("mission_description", "")).strip()
    if not desc:
        desc = "Step outside, disconnect from digital feeds, and observe the natural world around you."

    try:
        minutes = int(data.get("estimated_minutes", expected_minutes))
    except (ValueError, TypeError):
        minutes = expected_minutes

    raw_tasks = data.get("three_to_five_tasks", [])
    if not isinstance(raw_tasks, list) or len(raw_tasks) < 3:
        raise ValueError("Mission must contain at least three tasks")
    tasks = [str(t).strip() for t in raw_tasks if str(t).strip()][:5]
    if len(tasks) < 3:
        raise ValueError("Mission contains fewer than 3 valid tasks")

    raw_tips = data.get("observation_tips", [])
    if isinstance(raw_tips, list) and raw_tips:
        tips = [str(tip).strip() for tip in raw_tips if str(tip).strip()]
    else:
        tips = ["Look closely at small bark grooves and vein patterns on leaves.", "Close your eyes for 30 seconds to count distinct natural sounds."]

    reflection = str(data.get("one_reflection_question", "")).strip()
    if not reflection:
        reflection = "What was the most subtle detail in nature you only noticed after putting your screen away?"

    raw_safety = data.get("safety_reminders", [])
    if isinstance(raw_safety, list) and raw_safety:
        safety = [str(s).strip() for s in raw_safety if str(s).strip()]
    else:
        safety = ["Watch your footing on uneven surfaces.", "Respect wild habitats and do not touch unfamiliar thorns or wildlife."]

    low_screen = str(data.get("low_screen_mode_instruction", "")).strip()
    if not low_screen:
        low_screen = "Lock your phone, slip it in your pocket or bag, and observe with all your senses."

    return {
        "mission_title": title,
        "mission_description": desc,
        "estimated_minutes": minutes,
        "three_to_five_tasks": tasks,
        "observation_tips": tips,
        "one_reflection_question": reflection,
        "safety_reminders": safety,
        "low_screen_mode_instruction": low_screen,
    }


def get_fallback_mission(preferences: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
    """
    Produce a clearly marked sample mission when AI inference is unavailable.
    Never pretends to be generated by live Gemma model.
    """
    env = preferences.get("environment", "park").title()
    time_min = preferences.get("time_minutes", 15)
    diff = preferences.get("difficulty", "easy").title()
    interests = preferences.get("interests", ["plants", "mindful observation"])
    interest_str = ", ".join(interests) if isinstance(interests, list) else str(interests)

    fallback = {
        "mission_title": f"The Grounding Walk: {env} Exploration",
        "mission_description": (
            f"A curated sample {diff.lower()}-difficulty exploration designed for a {env.lower()} ({time_min} mins). "
            f"Focusing on {interest_str}. Step outside, slow your breathing, and leave notifications behind."
        ),
        "estimated_minutes": time_min,
        "three_to_five_tasks": [
            f"Find a spot in your {env.lower()} with green foliage. Stand still for 60 seconds and observe three distinct textures (smooth bark, ribbed leaf, soil).",
            "Listen carefully with eyes closed or relaxed to distinguish natural rustling or bird sounds from distant city hum.",
            f"Search for signs of wildlife or plant life coexisting with human structures (moss on pavement, ants on a tree trunk, flowering weeds).",
            "Pick up one fallen leaf or twig from the ground, study its branching pattern, and return it respectfully to the soil."
        ],
        "observation_tips": [
            "Scan at different levels: ground cover, eye level, and the canopy or open sky.",
            "Touch tree bark or soil gently to ground your senses in physical reality."
        ],
        "one_reflection_question": "How did your breathing and heart rate shift between being indoors and standing in the open air?",
        "safety_reminders": [
            "Stay aware of surrounding pathways, cyclists, and traffic.",
            "Do not consume or break wild plants; leave nature undisturbed."
        ],
        "low_screen_mode_instruction": "Pocket your device now. Set a gentle timer if needed, but keep your eyes on the horizon, not a screen.",
        "is_sample_fallback": True,
        "fallback_reason": reason or "Live AI service unconfigured or offline. This is a pre-designed sample mission for demonstration."
    }
    return fallback


def generate_mission(preferences: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    Generate an outdoor mission using Gemma.
    Returns:
        (mission_dict, is_live_ai_boolean)
    """
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMMA_MODEL_ID", "gemma-3-4b-it")

    if not key or not key.strip():
        # Clean honest fallback
        return get_fallback_mission(preferences, reason="No API key provided in environment variables."), False

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        user_prompt = (
            f"Generate a customized outdoor mission with the following user parameters:\n"
            f"- Environment: {preferences.get('environment', 'park')}\n"
            f"- Available Time: {preferences.get('time_minutes', 15)} minutes\n"
            f"- Difficulty: {preferences.get('difficulty', 'easy')}\n"
            f"- Interests: {', '.join(preferences.get('interests', [])) if isinstance(preferences.get('interests'), list) else preferences.get('interests')}\n"
            f"- User Instruction/Focus: {preferences.get('instruction', 'None')}\n\n"
            f"{JSON_SCHEMA_INSTRUCTION}"
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[user_prompt],
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SYSTEM,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        raw_text = response.text or ""
        cleaned = clean_json_text(raw_text)
        parsed = json.loads(cleaned)
        validated = validate_mission_schema(parsed, expected_minutes=int(preferences.get("time_minutes", 15)))
        validated["is_live_ai"] = True
        validated["model_engine"] = model_name
        return validated, True

    except Exception as exc:
        # Fallback gracefully with honest disclosure
        fallback = get_fallback_mission(
            preferences,
            reason=f"Model call failed ({type(exc).__name__}: {str(exc)[:120]}). Showing structured sample mission."
        )
        return fallback, False
