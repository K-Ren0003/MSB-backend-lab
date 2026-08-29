from fastapi.testclient import TestClient
from api.app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_event():
    response = client.post(
        "/events",
        json={
            "home_team_id": 1,
            "away_team_id": 2,
            "starts_at": "2026-08-30T18:00:00",
            "status": "scheduled"
        }
    )

    assert response.status_code == 201
    assert response.json()["home_team_id"] == 1
    assert response.json()["status"] == "scheduled"


def test_get_event():
    response = client.get("/events/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_invalid_event():
    response = client.get("/events/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}

def test_create_tip():
    response = client.post(
        "/tips",
        json={
            "user_id": 1,
            "event_id": 1,
            "predicted_winner_team_id": 1
        }
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == 1
    assert response.json()["event_id"] == 1