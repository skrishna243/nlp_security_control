import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PIN extraction
# ---------------------------------------------------------------------------

_PIN_KEYWORD_RE = re.compile(
    r"(?:pin|passcode|pass\s*code|password)\s*(?:is\s*|[:\s]+)?(\d{4,6})",
    re.IGNORECASE,
)
_PIN_BARE_RE = re.compile(r"\b(\d{4,6})\b")


def extract_pin(text: str) -> Optional[str]:
    # Prefer PIN adjacent to a keyword
    m = _PIN_KEYWORD_RE.search(text)
    if m:
        return m.group(1)
    # Fallback: first standalone 4-6 digit sequence
    m = _PIN_BARE_RE.search(text)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Name extraction
# ---------------------------------------------------------------------------

# Common non-name words to skip when searching for capitalised tokens
_NON_NAME_WORDS = {
    "I", "A", "The", "My", "Our", "Your", "His", "Her", "Its",
    "We", "They", "She", "He", "It", "You",
    "Please", "Now", "Today", "Sunday", "Monday", "Tuesday",
    "Wednesday", "Thursday", "Friday", "Saturday",
    "System", "Alarm", "Security", "User", "Arm", "Disarm", "Pin",
    "Passcode", "Access", "Mode", "Stay", "Away", "Home",
}

# Strategy 1: explicit "user/named/for NAME" pattern
# Captures a single name word (or hyphenated/apostrophe name like O'Brien, Mary-Jane)
# Does NOT capture spaces to prevent "John With Pin" false matches
_USER_KEYWORD_RE = re.compile(
    r"(?:user\s+|named?\s+|for\s+)([A-Z][a-z]+(?:[-'][A-Za-z][a-z]+)?)",
    re.IGNORECASE,
)

# Strategy 2: relationship/title words (mother-in-law, sister, friend, etc.)
_RELATIONSHIP_RE = re.compile(
    r"\b(?:my|our|the)\s+([A-Za-z]+-(?:in-)?law|[A-Za-z]+(?:\s+[A-Za-z]+)?)\b",
    re.IGNORECASE,
)

# Strategy 3: capitalized word near "pin" or "passcode" (but not common verbs)
# Avoid matching "Using", "Making", "Creating" by requiring lowercase after first letter
_NEAR_PIN_RE = re.compile(
    r"\b([A-Z][a-z]+(?:[-'][A-Za-z][a-z]+)?)\s*(?:[,.]?\s*)?(?:using\s+)?(?:pin|passcode|pass\s*code|password)",
    re.IGNORECASE,
)


def extract_name(text: str) -> Optional[str]:
    # Strategy 1: explicit keyword (add user John, name Sarah, for Alice)
    m = _USER_KEYWORD_RE.search(text)
    if m:
        candidate = m.group(1).strip()
        if candidate.title() not in _NON_NAME_WORDS and candidate.lower() not in {w.lower() for w in _NON_NAME_WORDS}:
            return candidate.title()

    # Strategy 2: relationship/title words (my mother-in-law, the sister, our friend)
    m = _RELATIONSHIP_RE.search(text)
    if m:
        candidate = m.group(1).strip()
        if candidate.title() not in _NON_NAME_WORDS and len(candidate) > 2:
            return candidate.replace(" ", "-").title()

    # Strategy 3: capitalized token before "pin/passcode" (prefer hyphenated names)
    m = _NEAR_PIN_RE.search(text)
    if m:
        candidate = m.group(1).strip()
        if candidate.title() not in _NON_NAME_WORDS:
            return candidate.title()

    return None


# ---------------------------------------------------------------------------
# Mode extraction
# ---------------------------------------------------------------------------

_MODE_PATTERNS: dict[str, re.Pattern] = {
    "stay": re.compile(r"\bstay\b", re.IGNORECASE),
    "home": re.compile(r"\bhome\b", re.IGNORECASE),
    "away": re.compile(r"\baway\b", re.IGNORECASE),
}


def extract_mode(text: str) -> str:
    for mode, pattern in _MODE_PATTERNS.items():
        if pattern.search(text):
            return mode
    return "away"


# ---------------------------------------------------------------------------
# Time range extraction (via dateparser)
# ---------------------------------------------------------------------------

_RANGE_RE = re.compile(
    r"from\s+(.+?)\s+to\s+(.+?)(?:\s*[,.]|$)",
    re.IGNORECASE | re.DOTALL,
)


def extract_time_range(text: str) -> tuple[Optional[str], Optional[str]]:
    try:
        import dateparser  # type: ignore

        m = _RANGE_RE.search(text)
        if not m:
            return None, None

        start_raw = m.group(1).strip()
        end_raw = m.group(2).strip()
        start_dt = dateparser.parse(start_raw)
        end_dt = dateparser.parse(end_raw)

        start_iso = start_dt.isoformat() if start_dt else None
        end_iso = end_dt.isoformat() if end_dt else None
        return start_iso, end_iso

    except Exception as exc:
        logger.warning("Time extraction failed: %s", exc)
        return None, None


# ---------------------------------------------------------------------------
# Permissions extraction
# ---------------------------------------------------------------------------

_ARM_AND_DISARM_RE = re.compile(r"\barm\s+and\s+disarm\b", re.IGNORECASE)
_CAN_ARM_RE = re.compile(
    r"\b(?:can|able\s+to|allow(?:ed)?\s+to|with\s+(?:full\s+)?access\s+to)\s+"
    r"((?:arm|disarm)(?:\s+and\s+(?:arm|disarm))?)\b",
    re.IGNORECASE,
)


def extract_permissions(text: str) -> list[str]:
    if _ARM_AND_DISARM_RE.search(text):
        return ["arm", "disarm"]

    perms: set[str] = set()
    m = _CAN_ARM_RE.search(text)
    if m:
        fragment = m.group(1).lower()
        if "arm" in fragment:
            perms.add("arm")
        if "disarm" in fragment:
            perms.add("disarm")

    return sorted(perms) if perms else ["arm", "disarm"]
