import pytest


class TestArmSystem:
    def test_arm_default(self, client):
        r = client.post("/api/arm-system", json={})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["state"]["armed"] is True
        assert data["state"]["mode"] == "away"

    def test_arm_stay_mode(self, client):
        r = client.post("/api/arm-system", json={"mode": "stay"})
        assert r.status_code == 200
        assert r.json()["state"]["mode"] == "stay"

    def test_arm_home_mode(self, client):
        r = client.post("/api/arm-system", json={"mode": "home"})
        assert r.status_code == 200
        assert r.json()["state"]["mode"] == "home"

    def test_arm_invalid_mode(self, client):
        r = client.post("/api/arm-system", json={"mode": "invalid"})
        assert r.status_code == 422


class TestDisarmSystem:
    def test_disarm(self, client):
        client.post("/api/arm-system", json={"mode": "away"})
        r = client.post("/api/disarm-system", json={})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["state"]["armed"] is False


class TestAddUser:
    def test_add_user_basic(self, client):
        r = client.post("/api/add-user", json={"name": "John", "pin": "4321"})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["user"]["name"] == "John"
        # PIN must be masked
        assert data["user"]["pin"] == "**21"

    def test_add_user_pin_masking(self, client):
        r = client.post("/api/add-user", json={"name": "Alice", "pin": "123456"})
        assert r.status_code == 200
        assert r.json()["user"]["pin"] == "****56"

    def test_add_user_invalid_pin_too_short(self, client):
        r = client.post("/api/add-user", json={"name": "Bob", "pin": "123"})
        assert r.status_code == 422

    def test_add_user_invalid_pin_non_digits(self, client):
        r = client.post("/api/add-user", json={"name": "Bob", "pin": "abcd"})
        assert r.status_code == 422

    def test_add_user_with_times(self, client):
        r = client.post(
            "/api/add-user",
            json={
                "name": "Sarah",
                "pin": "5678",
                "start_time": "2025-01-01T17:00:00Z",
                "end_time": "2025-01-05T10:00:00Z",
                "permissions": ["arm", "disarm"],
            },
        )
        assert r.status_code == 200

    def test_add_user_empty_name(self, client):
        r = client.post("/api/add-user", json={"name": "", "pin": "1234"})
        assert r.status_code == 422


class TestRemoveUser:
    def test_remove_by_name(self, client):
        client.post("/api/add-user", json={"name": "John", "pin": "4321"})
        r = client.post("/api/remove-user", json={"name": "John"})
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_remove_by_pin(self, client):
        client.post("/api/add-user", json={"name": "John", "pin": "4321"})
        r = client.post("/api/remove-user", json={"pin": "4321"})
        assert r.status_code == 200

    def test_remove_nonexistent(self, client):
        r = client.post("/api/remove-user", json={"name": "Nobody"})
        assert r.status_code == 404

    def test_remove_no_identifier(self, client):
        r = client.post("/api/remove-user", json={})
        assert r.status_code == 400


class TestListUsers:
    def test_list_empty(self, client):
        r = client.get("/api/list-users")
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["users"] == []
        assert data["count"] == 0

    def test_list_with_users(self, client):
        client.post("/api/add-user", json={"name": "Alice", "pin": "1111"})
        client.post("/api/add-user", json={"name": "Bob", "pin": "2222"})
        r = client.get("/api/list-users")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 2

    def test_list_all_pins_masked(self, client):
        client.post("/api/add-user", json={"name": "Alice", "pin": "1111"})
        r = client.get("/api/list-users")
        for user in r.json()["users"]:
            assert "1111" not in user["pin"]
