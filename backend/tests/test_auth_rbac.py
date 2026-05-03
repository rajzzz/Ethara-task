from fastapi.testclient import TestClient


def signup(client: TestClient, name: str, email: str, password: str = "password123") -> dict:
    response = client.post(
        "/auth/signup",
        json={"name": name, "email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


def login(client: TestClient, email: str, password: str = "password123") -> dict:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def create_project(client: TestClient, name: str = "Project A") -> dict:
    response = client.post("/projects", json={"name": name, "description": "Sample"})
    assert response.status_code == 201, response.text
    return response.json()


def create_task(client: TestClient, project_id: int, assignee_id: int | None = None) -> dict:
    payload = {
        "title": "Task 1",
        "description": "Work item",
        "status": "todo",
        "priority": "medium",
    }
    if assignee_id is not None:
        payload["assignee_id"] = assignee_id

    response = client.post(f"/projects/{project_id}/tasks", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_auth_login_me_refresh_flow(client: TestClient) -> None:
    signup(client, "Admin", "ADMIN@EXAMPLE.COM")

    # Case-insensitive login check.
    login(client, "admin@example.com")

    me_response = client.get("/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@example.com"

    # Send a one-off invalid access token while keeping the valid refresh cookie in the client jar.
    unauthorized_response = client.get("/auth/me", cookies={"access_token": "invalid-token"})
    assert unauthorized_response.status_code == 401

    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 200

    recovered_me_response = client.get("/auth/me")
    assert recovered_me_response.status_code == 200


def test_duplicate_email_is_case_insensitive(client: TestClient) -> None:
    signup(client, "One", "One@Example.com")

    duplicate_response = client.post(
        "/auth/signup",
        json={"name": "Two", "email": "one@example.com", "password": "password123"},
    )

    assert duplicate_response.status_code == 409


def test_member_can_only_update_assigned_task_status(client: TestClient) -> None:
    admin = signup(client, "Admin", "admin@ethara.dev")
    member = signup(client, "Member", "member@ethara.dev")

    login(client, "admin@ethara.dev")
    project = create_project(client)
    add_member_response = client.post(
        f"/projects/{project['id']}/members",
        json={"email": "member@ethara.dev", "role": "member"},
    )
    assert add_member_response.status_code == 201

    task = create_task(client, project["id"], assignee_id=admin["id"])

    login(client, "member@ethara.dev")
    forbidden_response = client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})
    assert forbidden_response.status_code == 403

    login(client, "admin@ethara.dev")
    reassign_response = client.patch(
        f"/projects/{project['id']}/tasks/{task['id']}",
        json={"assignee_id": member["id"]},
    )
    assert reassign_response.status_code == 200

    login(client, "member@ethara.dev")
    allowed_response = client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})
    assert allowed_response.status_code == 200
    assert allowed_response.json()["status"] == "done"


def test_validation_and_empty_patch_errors(client: TestClient) -> None:
    weak_password_response = client.post(
        "/auth/signup",
        json={"name": "User", "email": "user@example.com", "password": "short"},
    )
    assert weak_password_response.status_code == 422

    signup(client, "Admin", "admin2@ethara.dev")
    login(client, "admin2@ethara.dev")
    project = create_project(client, name="Project B")
    task = create_task(client, project["id"])

    empty_project_patch = client.patch(f"/projects/{project['id']}", json={})
    assert empty_project_patch.status_code == 400

    empty_task_patch = client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={})
    assert empty_task_patch.status_code == 400
