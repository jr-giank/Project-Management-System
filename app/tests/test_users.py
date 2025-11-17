
import json

from app.models.users import User
from app.routes.auth import create_auth_token

def get_token(session):

    manager_user = session.query(User).filter_by(email="manager@example.com").first()
    if not manager_user:
        manager_user = User(
            first_name="Manager",
            last_name="User",
            email="manager@example.com",
            role="manager",
            password="SecureP@ssword1"
        )
        session.add(manager_user)
        session.commit()

    token = create_auth_token(manager_user)

    return token

def test_create_user(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "role": "employee",
        "password": "SecureP@ssword1",
        "confirm_password": "SecureP@ssword1"
    }

    response = client.post("/api/users", data=json.dumps(data), headers=headers, content_type="application/json")

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["first_name"] == "Test"
    assert payload["last_name"] == "User"
    assert payload["email"] == "testuser@example.com"
    assert payload["role"] == "employee"

    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    assert user is not None
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.email == "testuser@example.com"
    assert user.role.value == "employee"


def test_create_user_no_field(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {
        "first_name": "Test",
        "last_name": "User",
        "role": "manager",
        "email": "testuser@example.com",
        "confirm_password": "SecureP@ssword1"
    }
    response = client.post("/api/users", data=json.dumps(data), headers=headers, content_type="application/json")
    assert response.status_code == 400
    assert "Missing field" in response.get_json()["error"]


def test_create_user_unique(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}

    user = User(
        first_name="Test", 
        last_name="User", 
        email="testing@example.com", 
        role="employee",
        password="SecureP@ssword1"
    )
    db_session.add(user)
    db_session.commit()

    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testing@example.com",
        "role": "manager",
        "password": "SecureP@ssword1",
        "confirm_password": "SecureP@ssword1"
    }

    response = client.post("/api/users", data=json.dumps(data), headers=headers, content_type="application/json")
    assert response.status_code == 400
    assert "Email already exists" in response.get_json()["error"]


def test_list_users_returns_all(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}

    db_session.add_all([
        User(
            first_name="User", 
            last_name="Test", 
            email="usertest@example.com", 
            role="manager",
            password="SecureP@ssword1"
        ),
    ])
    db_session.commit()

    response = client.get("/api/users/", headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert "data" in payload
    assert isinstance(payload['data'], list)
    assert len(payload['data']) >= 1
    emails = [user["email"] for user in payload['data']]
    assert "usertest@example.com" in emails


def test_get_user(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    user = User(
        first_name="Test", 
        last_name="User",
        email="testuser+1@example.com", 
        role="employee",
        password="SecureP@ssword1"
    )
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["first_name"] == "Test"
    assert payload["last_name"] == "User"
    assert payload["email"] == "testuser+1@example.com"
    assert payload["role"] == "employee"


def test_get_user_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/users/100", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


def test_get_user_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/users/abc", headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"


def test_update_user_success(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    user = User(
        first_name="juan", 
        last_name="Test", 
        email="juantest@example.com", 
        role="employee",
        password="SecureP@ssword1"
    )
    db_session.add(user)
    db_session.commit()

    data = {"first_name": "Pedro", "role": "manager"}
    response = client.put(
        f"/api/users/{user.id}",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["first_name"] == "Pedro"
    assert payload["role"] == "manager"
    updated = db_session.get(User, user.id)
    assert updated.first_name == "Pedro"
    assert updated.role.value == "manager"


def test_update_user_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {"first_name": "X"}
    response = client.put(
        "/api/users/100", 
        data=json.dumps(data),
        headers=headers,
        content_type="application/json"
    )
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


def test_update_user_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.put(
        "/api/users/abc", 
        data=json.dumps({"first_name": "Testing"}), 
        headers=headers,
        content_type="application/json"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"


def test_delete_user_success(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    user = User(
        first_name="Flask", 
        last_name="API",
        email="flasapi@example.com", 
        role="employee",
        password="SecureP@ssword1"
    )
    db_session.add(user)
    db_session.commit()

    response = client.delete(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == 200
    deleted = db_session.get(User, user.id)
    assert deleted is None


def test_delete_user_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.delete("/api/users/100", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


def test_delete_user_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.delete("/api/users/abc", headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"