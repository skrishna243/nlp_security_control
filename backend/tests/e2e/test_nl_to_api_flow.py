"""
End-to-end tests: natural language text → NLP parsing → API execution → state change.
These tests verify the complete pipeline from user input to system state.
"""

import pytest


class TestArmFlow:
    def test_arm_via_nl(self, client):
        r = client.post("/nl/execute", json={"text": "arm the system"})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["parsed"]["intent"] == "arm"
        assert data["api_result"]["state"]["armed"] is True

    def test_arm_stay_mode_via_nl(self, client):
        r = client.post(
            "/nl/execute", json={"text": "please activate the alarm to stay mode"}
        )
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "arm"
        assert data["api_result"]["state"]["mode"] == "stay"
        assert data["api_result"]["state"]["armed"] is True

    def test_disarm_via_nl(self, client):
        # Arm first, then disarm
        client.post("/api/arm-system", json={"mode": "away"})
        r = client.post("/nl/execute", json={"text": "turn off the alarm now"})
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "disarm"
        assert data["api_result"]["state"]["armed"] is False


class TestUserManagementFlow:
    def test_add_user_via_nl(self, client):
        r = client.post("/nl/execute", json={"text": "add user John with pin 4321"})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["parsed"]["intent"] == "add_user"
        # Verify user actually added
        users_r = client.get("/api/list-users")
        names = [u["name"].lower() for u in users_r.json()["users"]]
        assert "john" in names

    def test_add_temporary_user_via_nl(self, client):
        text = "add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am"
        r = client.post("/nl/execute", json={"text": text})
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "add_user"
        assert data["ok"] is True
        # Verify Sarah was added
        users_r = client.get("/api/list-users")
        names = [u["name"].lower() for u in users_r.json()["users"]]
        assert "sarah" in names

    def test_remove_user_via_nl(self, client):
        client.post("/api/add-user", json={"name": "John", "pin": "4321"})
        r = client.post("/nl/execute", json={"text": "remove user John"})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["parsed"]["intent"] == "remove_user"
        # Verify removed
        users_r = client.get("/api/list-users")
        names = [u["name"].lower() for u in users_r.json()["users"]]
        assert "john" not in names

    def test_list_users_via_nl(self, client):
        client.post("/api/add-user", json={"name": "Alice", "pin": "1111"})
        r = client.post("/nl/execute", json={"text": "show me all users"})
        assert r.status_code == 200
        data = r.json()
        assert data["parsed"]["intent"] == "list_users"
        assert data["api_result"]["count"] >= 1

    def test_mother_in_law_scenario(self, client):
        """
        The complex scenario from the spec: no explicit 'add user' phrase,
        uses pronoun reference and informal language. The heuristic (or LLM fallback)
        must correctly identify this as add_user with pin extraction.
        """
        text = (
            "My mother-in-law is coming to stay for the weekend, "
            "make sure she can arm and disarm our system using passcode 1234"
        )
        r = client.post("/nl/execute", json={"text": text})
        assert r.status_code == 200
        data = r.json()
        # Must classify as add_user
        assert data["parsed"]["intent"] == "add_user"
        # PIN must be extracted
        assert data["parsed"]["entities"].get("pin") is not None
        # And user should be added (even with unknown/generic name)
        assert data["ok"] is True


class TestFullWorkflow:
    def test_complete_security_workflow(self, client):
        """Full workflow: add user → arm → verify state → disarm → verify → remove user"""
        # 1. Add user
        r = client.post("/nl/execute", json={"text": "add user Alice with pin 2468"})
        assert r.json()["ok"] is True

        # 2. Arm system
        r = client.post("/nl/execute", json={"text": "arm the system"})
        assert r.json()["api_result"]["state"]["armed"] is True

        # 3. Verify via health
        r = client.get("/healthz")
        assert r.json()["system_state"]["armed"] is True

        # 4. Disarm
        r = client.post("/nl/execute", json={"text": "disarm the system"})
        assert r.json()["api_result"]["state"]["armed"] is False

        # 5. Remove user
        r = client.post("/nl/execute", json={"text": "remove user Alice"})
        assert r.json()["ok"] is True

        # 6. Verify empty list
        r = client.get("/api/list-users")
        assert r.json()["count"] == 0
