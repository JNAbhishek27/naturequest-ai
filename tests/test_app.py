"""
Backend test suite for NatureQuest AI.
Tests health endpoint, model status, validation, AI fallback, and mocks without requiring live API keys.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app
import ai_service


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Health check endpoint should return 200 and healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "NatureQuest AI"


def test_model_status_endpoint(client, monkeypatch):
    """Model status endpoint should report config state without leaking secrets."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    res = client.get("/api/model-status")
    assert res.status_code == 200
    data = res.get_json()
    assert "configured" in data
    assert "model_id" in data
    assert "engine" in data
    assert data["configured"] is False


def test_generate_missing_payload(client):
    """Empty or non-JSON requests should return 400."""
    res = client.post("/api/generate", data="not json", content_type="text/plain")
    assert res.status_code == 400


def test_generate_invalid_environment(client):
    """Invalid environment parameter returns 400."""
    payload = {
        "environment": "mars",
        "time_minutes": 15,
        "difficulty": "easy",
        "interests": ["plants"]
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 400
    assert "Invalid environment" in res.get_json()["error"]


def test_generate_invalid_time(client):
    """Time outside [10, 15, 30] returns 400."""
    payload = {
        "environment": "park",
        "time_minutes": 45,
        "difficulty": "easy",
        "interests": ["plants"]
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 400
    assert "Invalid time" in res.get_json()["error"]


def test_generate_invalid_difficulty(client):
    """Invalid difficulty returns 400."""
    payload = {
        "environment": "park",
        "time_minutes": 15,
        "difficulty": "extreme",
        "interests": ["plants"]
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 400
    assert "Invalid difficulty" in res.get_json()["error"]


def test_generate_missing_interests(client):
    """Missing or empty interests returns 400."""
    payload = {
        "environment": "park",
        "time_minutes": 15,
        "difficulty": "easy",
        "interests": []
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 400
    assert "Please select at least one nature interest" in res.get_json()["error"]


def test_fallback_mission_when_no_api_key(client, monkeypatch):
    """When API key is absent, returns clean sample mission labeled as fallback."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    payload = {
        "environment": "campus",
        "time_minutes": 15,
        "difficulty": "moderate",
        "interests": ["plants", "birds"],
        "instruction": "Look around courtyard"
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["is_live_ai"] is False
    mission = data["mission"]
    assert "Campus" in mission["mission_title"]
    assert len(mission["three_to_five_tasks"]) >= 3
    assert mission["is_sample_fallback"] is True
    assert "fallback_reason" in mission


def test_mocked_live_ai_generation(client, monkeypatch):
    """When API returns valid model output, it is parsed and validated cleanly."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_key")

    mock_json_content = json.dumps({
        "mission_title": "Urban Foliage Expedition",
        "mission_description": "Explore resilient trees and flowering plants in your neighborhood.",
        "estimated_minutes": 15,
        "three_to_five_tasks": [
            "Find a tree with textured bark and touch it.",
            "Spot a small flowering plant growing in a sidewalk crack.",
            "Listen for two distinct bird calls."
        ],
        "observation_tips": [
            "Look for small insects around flowering heads.",
            "Touch the underside of three different leaves."
        ],
        "one_reflection_question": "Which plant seemed the most resilient today?",
        "safety_reminders": [
            "Stay clear of traffic.",
            "Do not touch sharp or thorny plants."
        ],
        "low_screen_mode_instruction": "Pocket your phone now."
    })

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = f"```json\n{mock_json_content}\n```"
        mock_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_instance

        payload = {
            "environment": "neighborhood",
            "time_minutes": 15,
            "difficulty": "easy",
            "interests": ["plants", "trees"]
        }
        res = client.post("/api/generate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["is_live_ai"] is True
        mission = data["mission"]
        assert mission["mission_title"] == "Urban Foliage Expedition"
        assert len(mission["three_to_five_tasks"]) == 3
        assert mission["estimated_minutes"] == 15


def test_malformed_ai_response_triggers_graceful_fallback(client, monkeypatch):
    """If AI outputs broken or non-schema JSON, app gracefully falls back without crashing."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_key")

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON at all: { broken json"
        mock_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_instance

        payload = {
            "environment": "trail",
            "time_minutes": 30,
            "difficulty": "adventurous",
            "interests": ["weather", "birds"]
        }
        res = client.post("/api/generate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["is_live_ai"] is False  # Fallback triggered
        assert "Trail" in data["mission"]["mission_title"]
        assert data["mission"]["is_sample_fallback"] is True
