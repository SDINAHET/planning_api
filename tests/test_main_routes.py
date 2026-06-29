from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_api_people(monkeypatch):
    monkeypatch.setattr("app.main.load_people", lambda source: ["Bob", "Alice"])

    response = client.get("/api/people")

    assert response.status_code == 200
    assert response.json()["people"] == ["Alice", "Bob"]


def test_api_planning(monkeypatch):
    monkeypatch.setattr("app.main.get_schedule", lambda source, person: [
        {
            "jour": "Mercredi",
            "date": "2026-06-24",
            "horaire": "10h-12h",
            "mission": "Accueil",
            "lieu": "Accueil",
        }
    ])

    monkeypatch.setattr("app.main.add_talks_to_slots", lambda slots: slots)

    response = client.get("/api/planning/Stephane")

    assert response.status_code == 200
    assert response.json()["person"] == "Stephane"
    assert response.json()["total"] == 1


def test_api_planning_not_found(monkeypatch):
    monkeypatch.setattr("app.main.get_schedule", lambda source, person: [])

    response = client.get("/api/planning/Inconnu")

    assert response.status_code == 404


def test_api_planning_general(monkeypatch):
    monkeypatch.setattr("app.main.extract_general", lambda source: [
        {
            "jour": "Mercredi",
            "date": "2026-06-24",
            "horaire": "10h-12h",
            "mission": "Accueil",
            "lieu": "Accueil",
            "benevoles": ["Alice"],
            "talks": [],
        }
    ])

    monkeypatch.setattr("app.main.add_talks_to_slots", lambda slots: slots)

    response = client.get("/api/planning?jour=Mercredi&q=accueil")

    assert response.status_code == 200
    assert response.json()["type"] == "general"
    assert response.json()["total"] == 1
