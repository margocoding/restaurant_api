
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


class TestOrders:
    def test_create_order_requires_auth(self, client_no_auth):
        response = client_no_auth.post(
            "/api/orders",
            json={
                "customer_name": "Test User",
                "phone": "+1234567890",
                "address": "123 Test St",
                "items": [{"menu_item_id": 1, "quantity": 1}],
            },
        )
        assert response.status_code == 401

    def test_create_order_from_cart_requires_auth(self, client_no_auth):
        response = client_no_auth.post(
            "/api/orders/from-cart",
            json={"phone": "+1234567890", "address": "123 Test St"},
        )
        assert response.status_code == 401

    def test_create_order(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]
        item_price = menu_items[0]["price"]

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": item_id, "quantity": 2}],
        }

        response = client.post("/api/orders", json=order_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Test User"
        assert data["phone"] == "+1234567890"
        assert data["total_amount"] == item_price * 2
        assert data["status"] == "pending"

    def test_create_order_from_cart(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]
        item_price = menu_items[0]["price"]

        client.post(
            "/api/cart", json={"menu_item_id": item_id, "quantity": 2}, headers=headers
        )

        order_data = {"phone": "+1234567890", "address": "123 Test St"}

        response = client.post(
            "/api/orders/from-cart", json=order_data, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+1234567890"
        assert data["total_amount"] == item_price * 2
        assert data["status"] == "pending"

        cart_response = client.get("/api/cart", headers=headers)
        assert cart_response.json() == []

    def test_create_order_from_empty_cart(self, client):
        headers = get_auth_headers(client)

        order_data = {"phone": "+1234567890", "address": "123 Test St"}

        response = client.post(
            "/api/orders/from-cart", json=order_data, headers=headers
        )
        assert response.status_code == 400

    def test_create_order_with_invalid_item(self, client):
        headers = get_auth_headers(client)

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": 99999, "quantity": 1}],
        }

        response = client.post("/api/orders", json=order_data, headers=headers)
        assert response.status_code == 400

    def test_create_order_with_zero_quantity(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": item_id, "quantity": 0}],
        }

        response = client.post("/api/orders", json=order_data, headers=headers)
        assert response.status_code in [400, 422]

    def test_get_orders(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": item_id, "quantity": 1}],
        }

        client.post("/api/orders", json=order_data, headers=headers)

        response = client.get("/api/orders", headers=headers)
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) > 0

    def test_update_order_status(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": item_id, "quantity": 1}],
        }

        order_response = client.post("/api/orders", json=order_data, headers=headers)
        order_id = order_response.json()["id"]

        status_update = {"status": "confirmed"}
        response = client.patch(
            f"/api/orders/{order_id}/status", json=status_update, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_update_order_status_invalid(self, client):
        headers = get_auth_headers(client)

        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        order_data = {
            "customer_name": "Test User",
            "phone": "+1234567890",
            "address": "123 Test St",
            "items": [{"menu_item_id": item_id, "quantity": 1}],
        }

        order_response = client.post("/api/orders", json=order_data, headers=headers)
        order_id = order_response.json()["id"]

        status_update = {"status": "invalid_status"}
        response = client.patch(
            f"/api/orders/{order_id}/status", json=status_update, headers=headers
        )
        assert response.status_code == 400
