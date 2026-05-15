from fastapi.testclient import TestClient


def create_test_user(
    client: TestClient, username: str = "testuser", password: str = "testpass123"
):
    response = client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )
    return response


def login_user(
    client: TestClient, username: str = "testuser", password: str = "testpass123"
):
    response = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    return response


def get_auth_headers(
    client: TestClient, username: str = "testuser", password: str = "password123"
):
    login_response = login_user(client, username, password)
    if login_response.status_code != 200:
        raise RuntimeError(
            f"Login failed with status {login_response.status_code}: {login_response.text}"
        )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_register_user(self, client):
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert "message" in data

    def test_register_duplicate_user(self, client):
        create_test_user(client, "duplicateuser", "password123")
        response = client.post(
            "/api/auth/register",
            json={"username": "duplicateuser", "password": "password456"},
        )
        assert response.status_code == 400

    def test_login_success(self, client):
        create_test_user(client, "loginuser", "password123")
        response = client.post(
            "/api/auth/login", json={"username": "loginuser", "password": "password123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        create_test_user(client, "loginuser2", "password123")
        response = client.post(
            "/api/auth/login",
            json={"username": "loginuser2", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client_no_auth):
        response = client_no_auth.get("/api/cart")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client_no_auth):
        response = client_no_auth.get(
            "/api/cart", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
