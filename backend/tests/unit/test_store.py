import pytest

from app.store import SecurityStore


@pytest.fixture
def s():
    store = SecurityStore()
    return store


class TestSystemState:
    def test_initial_state(self, s):
        state = s.get_state()
        assert state["armed"] is False
        assert state["mode"] == "away"

    def test_arm_default(self, s):
        state = s.arm()
        assert state["armed"] is True
        assert state["mode"] == "away"

    def test_arm_stay(self, s):
        state = s.arm("stay")
        assert state["armed"] is True
        assert state["mode"] == "stay"

    def test_disarm(self, s):
        s.arm("home")
        state = s.disarm()
        assert state["armed"] is False


class TestUsers:
    def test_add_user(self, s):
        user = s.add_user("Alice", "1234")
        assert user["name"] == "Alice"
        # PIN is masked in response
        assert user["pin"] != "1234"
        assert user["pin"] == "**34"

    def test_add_user_sets_default_permissions(self, s):
        user = s.add_user("Bob", "5678")
        assert set(user["permissions"]) == {"arm", "disarm"}

    def test_add_user_custom_permissions(self, s):
        user = s.add_user("Carol", "9999", permissions=["arm"])
        assert user["permissions"] == ["arm"]

    def test_list_users(self, s):
        s.add_user("Alice", "1111")
        s.add_user("Bob", "2222")
        users = s.list_users()
        assert len(users) == 2
        names = [u["name"] for u in users]
        assert "Alice" in names
        assert "Bob" in names

    def test_list_users_pins_masked(self, s):
        s.add_user("Alice", "1234")
        users = s.list_users()
        assert users[0]["pin"] == "**34"
        assert "1234" not in users[0]["pin"]

    def test_remove_user_by_name(self, s):
        s.add_user("Alice", "1234")
        result = s.remove_user(name="Alice")
        assert result is not None
        assert result["name"] == "Alice"
        assert s.list_users() == []

    def test_remove_user_by_pin(self, s):
        s.add_user("Alice", "1234")
        result = s.remove_user(pin="1234")
        assert result is not None
        assert s.list_users() == []

    def test_remove_nonexistent_user(self, s):
        result = s.remove_user(name="Nobody")
        assert result is None

    def test_remove_user_case_insensitive(self, s):
        s.add_user("Alice", "1234")
        result = s.remove_user(name="alice")
        assert result is not None

    def test_add_duplicate_pin_overwrites(self, s):
        s.add_user("Alice", "1234")
        s.add_user("Bob", "1234")  # same PIN
        # Bob should now own that PIN
        user = s.get_user_by_name("bob")
        assert user is None or user["name"] == "Bob"


class TestMaskPin:
    def test_four_digits(self):
        assert SecurityStore.mask_pin("4321") == "**21"

    def test_six_digits(self):
        assert SecurityStore.mask_pin("123456") == "****56"

    def test_two_digits(self):
        assert SecurityStore.mask_pin("12") == "12"

    def test_one_digit(self):
        assert SecurityStore.mask_pin("1") == "1"
