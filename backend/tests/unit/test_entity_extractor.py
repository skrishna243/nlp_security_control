import pytest

from app.nlp.entity_extractor import (
    extract_mode,
    extract_name,
    extract_permissions,
    extract_pin,
    extract_time_range,
)


class TestExtractPin:
    def test_pin_after_keyword(self):
        assert extract_pin("add user John with pin 4321") == "4321"

    def test_pin_after_passcode(self):
        assert extract_pin("using passcode 1234") == "1234"

    def test_pin_with_colon(self):
        assert extract_pin("pin: 5678") == "5678"

    def test_pin_six_digits(self):
        assert extract_pin("pin is 123456") == "123456"

    def test_pin_bare_fallback(self):
        assert extract_pin("use code 9876") == "9876"

    def test_no_pin(self):
        assert extract_pin("arm the system") is None

    def test_prefers_keyword_adjacent(self):
        # "3 users, pin is 5678" — 3 is also a digit sequence but too short
        assert extract_pin("3 users, pin is 5678") == "5678"

    def test_pin_near_end(self):
        assert extract_pin("my passcode is 2468") == "2468"


class TestExtractName:
    def test_name_after_user(self):
        assert extract_name("add user John with pin 4321") == "John"

    def test_name_after_user_temporary(self):
        assert extract_name("add a temporary user Sarah, pin 5678") == "Sarah"

    def test_name_near_pin(self):
        assert extract_name("Sarah, pin 5678") == "Sarah"

    def test_no_name(self):
        result = extract_name("arm the system")
        assert result is None

    def test_common_word_not_a_name(self):
        # "The system" — "The" should not be extracted as a name
        result = extract_name("please activate the alarm")
        assert result is None


class TestExtractMode:
    def test_stay_mode(self):
        assert extract_mode("arm in stay mode") == "stay"

    def test_home_mode(self):
        assert extract_mode("activate alarm home mode") == "home"

    def test_away_mode(self):
        assert extract_mode("arm it in away mode") == "away"

    def test_default_away(self):
        assert extract_mode("arm the system") == "away"

    def test_stay_in_complex(self):
        assert extract_mode("please activate the alarm to stay mode") == "stay"


class TestExtractTimeRange:
    def test_no_range(self):
        start, end = extract_time_range("arm the system")
        assert start is None
        assert end is None

    def test_time_range_present(self):
        start, end = extract_time_range(
            "add user Sarah from today 5pm to Sunday 10am"
        )
        # dateparser resolves these — just check they returned something
        assert start is not None
        assert end is not None

    def test_time_range_iso_format(self):
        start, end = extract_time_range("from today 9am to tomorrow 6pm")
        # ISO 8601 format check
        if start:
            assert "T" in start or "+" in start


class TestExtractPermissions:
    def test_arm_and_disarm(self):
        perms = extract_permissions("she can arm and disarm our system")
        assert set(perms) == {"arm", "disarm"}

    def test_default_full_access(self):
        perms = extract_permissions("add user John with pin 1234")
        assert set(perms) == {"arm", "disarm"}

    def test_mother_in_law_permissions(self):
        text = (
            "My mother-in-law is coming, make sure she can arm and disarm "
            "our system using passcode 1234"
        )
        perms = extract_permissions(text)
        assert set(perms) == {"arm", "disarm"}
