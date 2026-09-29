import os
import tempfile
import pytest
import app as app_module


@pytest.fixture()
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    original_db = app_module.DB_NAME
    app_module.DB_NAME = db_path
    app_module.init_db(db_path)

    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.DB_NAME = original_db
    if os.path.exists(db_path):
        os.remove(db_path)


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_default_admin_login(client):
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    assert response.get_json()["role"] == "Admin"


def test_invalid_login(client):
    response = client.post(
        "/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_create_and_get_client(client):
    response = client.post(
        "/clients",
        json={
            "name": "John",
            "age": 30,
            "height": 175,
            "weight": 80,
            "membership_status": "Active",
        },
    )
    assert response.status_code == 201
    client_id = response.get_json()["id"]

    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.get_json()["name"] == "John"


def test_duplicate_client_rejected(client):
    payload = {"name": "John"}
    assert client.post("/clients", json=payload).status_code == 201
    assert client.post("/clients", json=payload).status_code == 409


def test_empty_client_name_rejected(client):
    response = client.post("/clients", json={"name": ""})
    assert response.status_code == 400


def test_program_generation(client):
    create = client.post("/clients", json={"name": "Jane"})
    client_id = create.get_json()["id"]

    response = client.post(
        f"/clients/{client_id}/program",
        json={"program_type": "Muscle Gain"},
    )
    assert response.status_code == 200
    assert response.get_json()["program_type"] == "Muscle Gain"
    assert response.get_json()["program"]


def test_invalid_program_type(client):
    create = client.post("/clients", json={"name": "Jane"})
    client_id = create.get_json()["id"]

    response = client.post(
        f"/clients/{client_id}/program",
        json={"program_type": "Invalid"},
    )
    assert response.status_code == 400


def test_membership(client):
    create = client.post(
        "/clients",
        json={
            "name": "Alex",
            "membership_status": "Active",
            "membership_end": "2026-12-31",
        },
    )
    client_id = create.get_json()["id"]

    response = client.get(f"/clients/{client_id}/membership")
    assert response.status_code == 200
    assert response.get_json()["membership_status"] == "Active"


def test_add_and_get_workout(client):
    create = client.post("/clients", json={"name": "Mike"})
    client_id = create.get_json()["id"]

    response = client.post(
        f"/clients/{client_id}/workouts",
        json={
            "date": "2026-09-29",
            "workout_type": "Strength",
            "duration_min": 60,
            "notes": "Upper body",
        },
    )
    assert response.status_code == 201

    response = client.get(f"/clients/{client_id}/workouts")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_workout_validation(client):
    create = client.post("/clients", json={"name": "Sam"})
    client_id = create.get_json()["id"]

    response = client.post(
        f"/clients/{client_id}/workouts",
        json={"workout_type": "Cardio"},
    )
    assert response.status_code == 400
