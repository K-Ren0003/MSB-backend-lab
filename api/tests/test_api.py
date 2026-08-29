def create_teams(client):
    home = client.post("/teams", json={"name": "Broncos", "code": "BRI"})
    away = client.post("/teams", json={"name": "Storm", "code": "MEL"})
    assert home.status_code == 201
    assert away.status_code == 201
    return home.json(), away.json()


def create_event(client):
    home, away = create_teams(client)
    response = client.post(
        "/events",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "starts_at": "2026-08-30T18:00:00",
            "status": "scheduled",
        },
    )
    assert response.status_code == 201
    return response.json(), home, away


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_retrieve_event_from_separate_sessions(client):
    event, _home, _away = create_event(client)

    response = client.get(f"/events/{event['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == event["id"]
    assert response.json()["status"] == "scheduled"


def test_get_invalid_event(client):
    response = client.get("/events/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}


def test_invalid_event_status_returns_validation_error(client):
    home, away = create_teams(client)
    response = client.post(
        "/events",
        json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "starts_at": "2026-08-30T18:00:00",
            "status": "not-a-real-status",
        },
    )
    assert response.status_code == 422


def test_create_tip_persists_relations_and_activity_event(
    client,
    fake_activity_collection,
):
    event, home, _away = create_event(client)
    user_response = client.post(
        "/users",
        json={"display_name": "Kaden", "email": "kaden@example.com"},
    )
    assert user_response.status_code == 201
    user = user_response.json()

    tip_response = client.post(
        "/tips",
        json={
            "user_id": user["id"],
            "event_id": event["id"],
            "predicted_winner_team_id": home["id"],
        },
    )
    assert tip_response.status_code == 201
    tip = tip_response.json()

    user_tips = client.get(f"/users/{user['id']}/tips")
    assert user_tips.status_code == 200
    assert user_tips.json()[0]["id"] == tip["id"]

    activity_response = client.get("/activity-events")
    assert activity_response.status_code == 200
    assert activity_response.json()[0]["event_type"] == "tip.created"
    assert activity_response.json()[0]["event_id"] == event["id"]
    assert len(fake_activity_collection.documents) == 1


def test_activity_event_limit_is_validated(client):
    response = client.get("/activity-events?limit=0")
    assert response.status_code == 422
