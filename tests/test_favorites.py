
def get_auth_headers(client, username: str = "testuser", password: str = "password123"):
    login_response = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    if login_response.status_code != 200:
        raise RuntimeError(
            f"Login failed with status {login_response.status_code}: {login_response.text}"
        )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFavorites:
    def test_get_favorites_empty(self, client):
        headers = get_auth_headers(client)
        response = client.get("/api/favorites", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_add_item_to_favorites(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        assert len(menu_items) > 0
        item_id = menu_items[0]["id"]

        response = client.post(
            "/api/favorites", json={"menu_item_id": item_id}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["menu_item_id"] == item_id

    def test_add_nonexistent_item_to_favorites(self, client):
        headers = get_auth_headers(client)
        response = client.post(
            "/api/favorites", json={"menu_item_id": 99999}, headers=headers
        )
        assert response.status_code == 404

    def test_add_duplicate_favorite(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post("/api/favorites", json={"menu_item_id": item_id}, headers=headers)
        response = client.post(
            "/api/favorites", json={"menu_item_id": item_id}, headers=headers
        )
        assert response.status_code == 400

    def test_remove_from_favorites(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        fav_response = client.post(
            "/api/favorites", json={"menu_item_id": item_id}, headers=headers
        )
        favorite_id = fav_response.json()["id"]

        response = client.delete(f"/api/favorites/{favorite_id}", headers=headers)
        assert response.status_code == 200

        favorites_response = client.get("/api/favorites", headers=headers)
        assert favorites_response.json() == []

    def test_favorites_isolation_between_users(self, client):
        client.post(
            "/api/auth/register",
            json={"username": "favuser1", "password": "password123"},
        )
        client.post(
            "/api/auth/register",
            json={"username": "favuser2", "password": "password123"},
        )

        headers1 = get_auth_headers(client, "favuser1", "password123")
        headers2 = get_auth_headers(client, "favuser2", "password123")

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post("/api/favorites", json={"menu_item_id": item_id}, headers=headers1)
        client.post("/api/favorites", json={"menu_item_id": item_id}, headers=headers2)

        fav1 = client.get("/api/favorites", headers=headers1).json()
        fav2 = client.get("/api/favorites", headers=headers2).json()

        assert len(fav1) == 1
        assert len(fav2) == 1
