class TestMenu:
    def test_get_menu(self, client):
        response = client.get("/api/menu")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_menu_item(self, client):
        menu_response = client.get("/api/menu")
        menu_items = menu_response.json()
        item_id = menu_items[0]["id"]

        response = client.get(f"/api/menu/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id

    def test_get_nonexistent_menu_item(self, client):
        response = client.get("/api/menu/99999")
        assert response.status_code == 404

    def test_get_categories(self, client):
        response = client.get("/api/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_menu(self, client):
        response = client.get("/api/menu?search=Пицца")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_menu_by_category(self, client):
        response = client.get("/api/menu?category=Пицца")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
