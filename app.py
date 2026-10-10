"""
NatureQuest AI Flask Application.
Serves frontend templates, validates parameters, and exposes API endpoints
for outdoor mission generation, status checks, and health.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load local environment if .env exists
load_dotenv()

from ai_service import generate_mission, get_model_status

app = Flask(__name__)

VALID_ENVIRONMENTS = {"garden", "park", "campus", "neighborhood", "trail"}
VALID_TIMES = {10, 15, 30}
VALID_DIFFICULTIES = {"easy", "moderate", "adventurous"}
VALID_INTERESTS = {"plants", "birds", "insects", "trees", "weather", "mindful observation"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "NatureQuest AI",
        "version": "1.0.0"
    }), 200


@app.route("/api/model-status")
def model_status():
    status = get_model_status()
    return jsonify(status), 200


@app.route("/api/generate", methods=["POST"])
def generate():
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload format"}), 400

    # Validate environment
    env = str(data.get("environment", "")).lower().strip()
    if env not in VALID_ENVIRONMENTS:
        return jsonify({
            "error": f"Invalid environment '{env}'. Must be one of: {', '.join(sorted(VALID_ENVIRONMENTS))}"
        }), 400

    # Validate time_minutes
    try:
        time_minutes = int(data.get("time_minutes", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Time must be an integer (10, 15, or 30)"}), 400

    if time_minutes not in VALID_TIMES:
        return jsonify({
            "error": f"Invalid time {time_minutes}. Allowed options: 10, 15, or 30 minutes."
        }), 400

    # Validate difficulty
    diff = str(data.get("difficulty", "")).lower().strip()
    if diff not in VALID_DIFFICULTIES:
        return jsonify({
            "error": f"Invalid difficulty '{diff}'. Must be one of: {', '.join(sorted(VALID_DIFFICULTIES))}"
        }), 400

    # Validate interests
    raw_interests = data.get("interests", [])
    if isinstance(raw_interests, str):
        raw_interests = [raw_interests]
    if not isinstance(raw_interests, list) or len(raw_interests) == 0:
        return jsonify({"error": "Please select at least one nature interest."}), 400

    cleaned_interests = []
    for item in raw_interests:
        clean_item = str(item).lower().strip()
        if clean_item in VALID_INTERESTS and clean_item not in cleaned_interests:
            cleaned_interests.append(clean_item)

    if not cleaned_interests:
        return jsonify({
            "error": "No valid interests selected. Please pick from: plants, birds, insects, trees, weather, mindful observation."
        }), 400

    # Validate optional instruction
    instruction = str(data.get("instruction", "")).strip()
    if len(instruction) > 280:
        return jsonify({"error": "Instruction text is too long (max 280 characters)."}), 400

    preferences = {
        "environment": env,
        "time_minutes": time_minutes,
        "difficulty": diff,
        "interests": cleaned_interests,
        "instruction": instruction
    }

    mission, is_live_ai = generate_mission(preferences)
    return jsonify({
        "success": True,
        "is_live_ai": is_live_ai,
        "mission": mission
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Production should run gunicorn app:app, but debug runner binds properly
    app.run(host="0.0.0.0", port=port, debug=False)
