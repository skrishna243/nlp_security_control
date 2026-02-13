import pytest

from app.nlp.rule_engine import classify_intent


@pytest.mark.parametrize(
    "text,expected",
    [
        # Required test phrases from spec
        ("arm the system", "arm"),
        ("please activate the alarm to stay mode", "arm"),
        ("turn off the alarm now", "disarm"),
        ("add user John with pin 4321", "add_user"),
        ("add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am", "add_user"),
        ("remove user John", "remove_user"),
        ("show me all users", "list_users"),
        # The complex mother-in-law case — heuristic should catch it
        (
            "My mother-in-law is coming to stay for the weekend, "
            "make sure she can arm and disarm our system using passcode 1234",
            "add_user",
        ),
        # Additional arm variants
        ("activate alarm", "arm"),
        ("lock it down", "arm"),
        ("turn on the alarm", "arm"),
        ("enable the security system", "arm"),
        # Additional disarm variants
        ("disarm the system", "disarm"),
        ("deactivate the alarm", "disarm"),
        ("disable the security", "disarm"),
        ("turn off the security", "disarm"),
        ("unlock the system", "disarm"),
        # Additional add_user variants
        ("create a user Bob with passcode 9999", "add_user"),
        ("give John access", "add_user"),
        # Additional remove_user variants
        ("delete user Alice", "remove_user"),
        ("revoke user access for Bob", "remove_user"),
        # Additional list_users variants
        ("list all users", "list_users"),
        ("who has access", "list_users"),
        ("show all users", "list_users"),
        # Edge cases
        ("", None),
        ("hello there", None),
        ("what time is it", None),
        # "arm and disarm" in context must NOT trigger arm intent
        ("she can arm and disarm using pin 1234", "add_user"),
    ],
)
def test_classify_intent(text: str, expected):
    assert classify_intent(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        # Ali Baba / Sesame
        ("open sesame", "disarm"),
        ("sesame open", "disarm"),
        ("sesame close", "arm"),
        ("close sesame", "arm"),
        # English creative aliases
        ("all clear", "disarm"),
        ("stand down", "disarm"),
        ("at ease", "disarm"),
        ("code red", "arm"),
        ("red alert", "arm"),
        ("go hot", "arm"),
        # Spanish
        ("armar el sistema", "arm"),
        ("activar el sistema", "arm"),
        ("desarmar el sistema", "disarm"),
        ("desactivar el sistema", "disarm"),
        ("mostrar usuarios", "list_users"),
        # French
        ("armer le système", "arm"),
        ("désarmer le système", "disarm"),
        # German
        ("scharf schalten", "arm"),
        ("Anlage scharf", "arm"),
        ("unscharf schalten", "disarm"),
        ("Anlage unscharf", "disarm"),
        # Arabic romanized
        ("aghliq", "arm"),
        ("iftah", "disarm"),
        ("aftah", "disarm"),
        # Hindi romanized
        ("band karo", "arm"),
        ("kholo", "disarm"),
        # Japanese romanized
        ("kagi kakete", "arm"),
        ("akete", "disarm"),
        # Portuguese
        ("armar o sistema", "arm"),
        ("desarmar o sistema", "disarm"),
    ],
)
def test_creative_aliases(text: str, expected: str):
    assert classify_intent(text) == expected


def test_new_phrases():
    assert classify_intent("shut off the alarm") == "disarm"
    assert classify_intent("start the alarm") == "arm"
