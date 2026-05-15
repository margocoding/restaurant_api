from backend.main import app
from backend.models import UserModel


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


class TestCart:
    def test_get_cart_empty(self, client):
        headers = get_auth_headers(client)
        response = client.get("/api/cart", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_add_item_to_cart(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        assert len(menu_items) > 0
        item_id = menu_items[0]["id"]

        response = client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 2}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["menu_item_id"] == item_id
        assert data["quantity"] == 2

    def test_add_nonexistent_item_to_cart(self, client):
        headers = get_auth_headers(client)
        response = client.post(
            "/api/cart", json={"menu_item_id": 99999, "quantity": 1}, headers=headers
        )
        assert response.status_code == 404

    def test_update_cart_item_quantity(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 1}, headers=headers
        )

        cart_response = client.get("/api/cart", headers=headers)
        cart_item_id = cart_response.json()[0]["id"]

        response = client.put(
            f"/api/cart/{cart_item_id}", json={"quantity": 5}, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 5

    def test_remove_item_from_cart(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 1}, headers=headers
        )

        cart_response = client.get("/api/cart", headers=headers)
        cart_item_id = cart_response.json()[0]["id"]

        response = client.delete(f"/api/cart/{cart_item_id}", headers=headers)
        assert response.status_code == 200

        cart_response = client.get("/api/cart", headers=headers)
        assert cart_response.json() == []

    def test_clear_cart(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()

        for item in menu_items[:3]:
            client.post(
                "/api/cart",
                json={"menu_item_id": item["id"], "quantity": 1},
                headers=headers,
            )

        cart_response = client.get("/api/cart", headers=headers)
        assert len(cart_response.json()) == 3

        response = client.delete("/api/cart", headers=headers)
        assert response.status_code == 200

        cart_response = client.get("/api/cart", headers=headers)
        assert cart_response.json() == []

    def test_add_same_item_twice_increases_quantity(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 2}, headers=headers
        )
        client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 3}, headers=headers
        )

        cart_response = client.get("/api/cart", headers=headers)
        assert len(cart_response.json()) == 1
        assert cart_response.json()[0]["quantity"] == 5

    def test_cart_isolation_between_users(self, db_session, client):
        from backend.auth import get_password_hash

        user1 = UserModel(
            username="cartuser1",
            hashed_password=get_password_hash("password123"),
            role="user",
        )
        user2 = UserModel(
            username="cartuser2",
            hashed_password=get_password_hash("password123"),
            role="user",
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()

        def get_user1():
            return (
                db_session.query(UserModel)
                .filter(UserModel.username == "cartuser1")
                .first()
            )

        def get_user2():
            return (
                db_session.query(UserModel)
                .filter(UserModel.username == "cartuser2")
                .first()
            )

        from backend.auth import get_current_user
        from backend.models import get_db

        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = get_user1

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        client.post("/api/cart", json={"menu_item_id": item_id, "quantity": 1})

        app.dependency_overrides[get_current_user] = get_user2
        client.post("/api/cart", json={"menu_item_id": item_id, "quantity": 2})

        cart1 = client.get("/api/cart").json()

        app.dependency_overrides[get_current_user] = get_user1
        cart1 = client.get("/api/cart").json()

        app.dependency_overrides[get_current_user] = get_user2
        cart2 = client.get("/api/cart").json()

        assert len(cart1) == 1
        assert len(cart2) == 1
        assert cart1[0]["quantity"] == 1
        assert cart2[0]["quantity"] == 2

        app.dependency_overrides.clear()
