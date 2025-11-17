
import json

from app.models.projects import Project
from app.models.users import User
from app.models.tasks import Task
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

def test_create_project(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {
        "name": "Project #1",
        "description": "Test project description"
    }

    response = client.post("/api/projects", data=json.dumps(data), headers=headers, content_type="application/json")

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["name"] == "Project #1"
    assert payload["description"] == "Test project description"

    project = db_session.query(Project).filter_by(name="Project #1").first()
    assert project is not None
    assert project.name == "Project #1"


def test_create_project_missing_field(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {"description": "Missing name"}
    response = client.post("/api/projects", data=json.dumps(data), headers=headers, content_type="application/json")
    assert response.status_code == 400
    assert "Missing field" in response.get_json()["error"]


def test_list_projects(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    db_session.add_all([
        Project(name="Project #1", description="desc"),
    ])
    db_session.commit()

    response = client.get("/api/projects", headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload['data'], list)
    assert any(p["name"] == "Project #1" for p in payload['data'])


def test_get_project(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Project #1", description="desc")
    db_session.add(project)
    db_session.commit()

    response = client.get(f"/api/projects/{project.id}", headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Project #1"
    assert payload["description"] == "desc"


def test_get_project_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/projects/100", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Project not found"


def test_get_project_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/projects/abc", headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"


def test_update_project_success(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Old Project", description="Old desc")
    db_session.add(project)
    db_session.commit()

    data = {"name": "New Project", "description": "Updated desc"}
    response = client.put(f"/api/projects/{project.id}", data=json.dumps(data), headers=headers,  content_type="application/json")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "New Project"
    updated = db_session.get(Project, project.id)
    assert updated.name == "New Project"


def test_update_project_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {"name": "Does not exist"}
    response = client.put("/api/projects/999", data=json.dumps(data), headers=headers, content_type="application/json")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Project not found"


def test_update_project_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    data = {"name": "Invalid ID"}
    response = client.put("/api/projects/abc", data=json.dumps(data), headers=headers, content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"


def test_delete_project_success(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Delete Project", description="desc")
    db_session.add(project)
    db_session.commit()

    response = client.delete(f"/api/projects/{project.id}", headers=headers)
    assert response.status_code == 200
    assert db_session.get(Project, project.id) is None


def test_delete_project_not_found(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.delete("/api/projects/999", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Project not found"


def test_delete_project_invalid_id(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.delete("/api/projects/abc", headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"


def test_create_task_under_project(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Project #1", description="desc")
    db_session.add(project)
    db_session.commit()

    data = {
        "title": "Task #1",
        "description": "Task under Project #1"
    }
    response = client.post(
        f"/api/projects/{project.id}/tasks",
        data=json.dumps(data), headers=headers,
        content_type="application/json"
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["title"] == "Task #1"
    assert payload["project_id"] == project.id

    task = db_session.query(Task).filter_by(title="Task #1").first()
    assert task is not None
    assert task.project_id == project.id


def test_create_task_missing_field(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Project #1", description="desc")
    db_session.add(project)
    db_session.commit()

    data = {"description": "Missing title"}
    response = client.post(
        f"/api/projects/{project.id}/tasks",
        data=json.dumps(data), headers=headers,
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "Missing field" in response.get_json()["error"]


def test_get_tasks_under_project(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    project = Project(name="Project #1", description="desc")
    db_session.add(project)
    db_session.commit()

    db_session.add(Task(title="Task #1", description="desc", project_id=project.id))
    db_session.commit()

    response = client.get(f"/api/projects/{project.id}/tasks", headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload['data'], list)
    assert len(payload['data']) == 1
    assert payload['data'][0]["title"] == "Task #1"


def test_get_tasks_invalid_project(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/projects/999/tasks", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Project not found"


def test_get_tasks_invalid_id_format(client, db_session):
    headers = {"Authorization": f"Bearer {get_token(db_session)}"}
    response = client.get("/api/projects/abc/tasks", headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid ID format"
