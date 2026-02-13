import pytest


class TestNLExecute:
    def test_empty_text(self, client):
        r = client.post("/nl/execute", json={"text": ""})
        assert r.status_code == 400

    def test_whitespace_text(self, client):
        r = client.post("/nl/execute", json={"text": "   "})
        assert r.status_code == 400

    def test_arm_command(self, client):
        r = client.post("/nl/execute", json={"text": "arm the system"})
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "arm"
        assert data["parsed"]["source"] == "rule"

    def test_disarm_command(self, client):
        r = client.post("/nl/execute", json={"text": "turn off the alarm now"})
        assert r.status_code == 200
        assert r.json()["parsed"]["intent"] == "disarm"

    def test_add_user_command(self, client):
        r = client.post("/nl/execute", json={"text": "add user John with pin 4321"})
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "add_user"

    def test_remove_user_command(self, client):
        client.post("/api/add-user", json={"name": "John", "pin": "4321"})
        r = client.post("/nl/execute", json={"text": "remove user John"})
        assert r.status_code == 200
        assert r.json()["parsed"]["intent"] == "remove_user"

    def test_list_users_command(self, client):
        r = client.post("/nl/execute", json={"text": "show me all users"})
        assert r.status_code == 200
        assert r.json()["parsed"]["intent"] == "list_users"

    def test_unknown_command_returns_error(self, client):
        r = client.post("/nl/execute", json={"text": "hello world"})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is False
        assert data["error"] is not None

    def test_response_structure(self, client):
        r = client.post("/nl/execute", json={"text": "arm the system"})
        data = r.json()
        assert "ok" in data
        assert "parsed" in data
        assert "api_result" in data
        assert "error" in data
        assert "text" in data["parsed"]
        assert "intent" in data["parsed"]
        assert "entities" in data["parsed"]
        assert "api" in data["parsed"]
        assert "source" in data["parsed"]
