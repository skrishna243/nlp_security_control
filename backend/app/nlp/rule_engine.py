import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Creative & multilingual aliases — checked BEFORE standard patterns
# Each entry: (compiled_pattern, intent)
# These are checked in order; first match wins.
# ---------------------------------------------------------------------------
CREATIVE_ALIASES: list[tuple[re.Pattern, str]] = [
    # ---- Ali Baba / Sesame ------------------------------------------------
    # "open sesame" / "sesame open" → disarm (open the door)
    (re.compile(r"\bopen\s+sesame\b|\bsesame\s+open\b", re.IGNORECASE), "disarm"),
    # "sesame close" / "close sesame" → arm (seal the cave)
    (re.compile(r"\bsesame\s+close\b|\bclose\s+sesame\b|\bsesame\s+shut\b", re.IGNORECASE), "arm"),

    # ---- English creative aliases ----------------------------------------
    (re.compile(r"\ball\s+clear\b|\bstand\s+down\b|\bat\s+ease\b|\bstand\s+easy\b", re.IGNORECASE), "disarm"),
    (re.compile(r"\bcode\s+red\b|\bred\s+alert\b|\bgo\s+hot\b|\bhigh\s+alert\b|\bgo\s+live\b", re.IGNORECASE), "arm"),

    # ---- Spanish -----------------------------------------------------------
    # armar/activar el sistema → arm; desarmar/desactivar → disarm
    (re.compile(r"\b(?:armar?|activ[ao]r?)\s+(?:el\s+)?sistema\b", re.IGNORECASE), "arm"),
    (re.compile(r"\b(?:desarmar?|desactiv[ao]r?)\s+(?:el\s+)?sistema\b", re.IGNORECASE), "disarm"),
    # mostrar usuarios → list_users
    (re.compile(r"\bmostrar?\s+(?:los\s+)?usuarios?\b", re.IGNORECASE), "list_users"),

    # ---- French ------------------------------------------------------------
    (re.compile(r"\b(?:armer?|activer?)\s+(?:le\s+)?syst[eè]me\b", re.IGNORECASE), "arm"),
    (re.compile(r"\b(?:d[eé]sarmer?|d[eé]sactiver?)\s+(?:le\s+)?syst[eè]me\b", re.IGNORECASE), "disarm"),

    # ---- German ------------------------------------------------------------
    # "scharf schalten" / "Anlage scharf" → arm
    (re.compile(r"\b(?:scharf\s+(?:schalten|machen)|anlage\s+scharf|alarm\s+scharf)\b", re.IGNORECASE), "arm"),
    # "unscharf schalten" / "Anlage unscharf" → disarm
    (re.compile(r"\b(?:unscharf\s+(?:schalten|machen)|anlage\s+unscharf|alarm\s+unscharf)\b", re.IGNORECASE), "disarm"),

    # ---- Hebrew (romanized) ------------------------------------------------
    # "pe'al" = activate, "batel" = cancel
    (re.compile(r"\bpe[''ʼ]?al\b|\bpa[''ʼ]?al\b", re.IGNORECASE), "arm"),
    (re.compile(r"\bbatel\b|\bbattel\b", re.IGNORECASE), "disarm"),

    # ---- Arabic (romanized) ------------------------------------------------
    # "aghliq" / "aghleq" = close/lock → arm; "iftah" / "aftah" = open → disarm
    (re.compile(r"\b(?:aghliq|aghleq|ughliq)\b", re.IGNORECASE), "arm"),
    (re.compile(r"\b(?:iftah|aftah|af-tah)\b", re.IGNORECASE), "disarm"),

    # ---- Hindi (romanized) -------------------------------------------------
    # "band karo" = lock/close it → arm; "kholo" = open → disarm
    (re.compile(r"\bband\s+karo\b|\bband\s+kar\b|\bband\s+karna\b", re.IGNORECASE), "arm"),
    (re.compile(r"\bkholo\b|\bkhol\s+do\b", re.IGNORECASE), "disarm"),

    # ---- Japanese (romanized) ----------------------------------------------
    # "kagi kakete" = lock it; "kagi hazushite" / "akete" = unlock
    (re.compile(r"\bkagi\s+kakete\b|\brokkushite\b", re.IGNORECASE), "arm"),
    (re.compile(r"\bakete\b|\bkagi\s+hazushite\b|\bunrokku\b", re.IGNORECASE), "disarm"),

    # ---- Portuguese --------------------------------------------------------
    (re.compile(r"\b(?:armar?|ativar?)\s+(?:o\s+)?sistema\b", re.IGNORECASE), "arm"),
    (re.compile(r"\b(?:desarmar?|desativar?)\s+(?:o\s+)?sistema\b", re.IGNORECASE), "disarm"),
]

# ---------------------------------------------------------------------------
# Standard intent patterns — ordered by priority
# add_user MUST come before arm/disarm to avoid "arm and disarm" misclassification
# ---------------------------------------------------------------------------
INTENT_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "add_user",
        re.compile(
            r"add\s+(?:a\s+)?(?:temporary\s+|temp\s+)?user"
            r"|create\s+(?:a\s+)?(?:temporary\s+)?user"
            r"|give\s+(?:\w+\s+)?access"
            r"|set\s*up\s+(?:a\s+)?(?:new\s+)?user"
            # "arm and disarm" = permission-grant language = add_user context
            r"|\barm\s+and\s+disarm\b",
            re.IGNORECASE,
        ),
    ),
    (
        "remove_user",
        re.compile(
            r"(?:remove|delete|revoke)\s+(?:the\s+)?(?:user|access(?:\s+for|\s+of)?)"
            r"|remove\s+\w+\s+from",
            re.IGNORECASE,
        ),
    ),
    (
        "list_users",
        re.compile(
            r"(?:show|list|display|get)\s+(?:me\s+)?(?:all\s+)?users?"
            r"|who\s+(?:has|have)\s+access"
            r"|show\s+(?:me\s+)?(?:the\s+)?user\s+list"
            r"|list\s+all\s+users?"
            r"|all\s+users?",
            re.IGNORECASE,
        ),
    ),
    (
        "disarm",
        re.compile(
            r"\b(?:disarm|deactivate|disable)\b"
            r"|turn\s+off\s+(?:the\s+)?(?:alarm|security|system)"
            r"|shut\s+off\s+(?:the\s+)?(?:alarm|security|system)"
            r"|unlock\s+(?:the\s+)?(?:system|alarm|security)?",
            re.IGNORECASE,
        ),
    ),
    (
        "arm",
        re.compile(
            # Negative lookahead prevents "arm and disarm" from matching
            r"\b(?:arm|activate|enable|lock\s+(?:it\s+)?down)\b(?!\s+and\s+disarm)"
            r"|turn\s+on\s+(?:the\s+)?(?:alarm|security|system)"
            r"|start\s+(?:the\s+)?(?:alarm|security|system)"
            r"|please\s+activate",
            re.IGNORECASE,
        ),
    ),
]

# Heuristic fallback: text mentions a PIN-like number with passcode/pin language
# but has no explicit "add user" phrase — e.g. "My mother-in-law ... passcode 1234"
ADD_USER_HEURISTIC = re.compile(
    r"\b(?:pin|passcode|pass\s*code|password)\b.{0,60}\b\d{4,6}\b"
    r"|\b\d{4,6}\b.{0,60}\b(?:pin|passcode|pass\s*code|password)\b",
    re.IGNORECASE | re.DOTALL,
)


def classify_intent(text: str) -> Optional[str]:
    if not text or not text.strip():
        return None

    # Check creative / multilingual aliases first
    for pattern, intent in CREATIVE_ALIASES:
        if pattern.search(text):
            logger.debug(
                "Intent classified via creative alias",
                extra={"intent": intent},
            )
            return intent

    # Check explicit add_user/remove_user/list_users patterns (before arm/disarm)
    for intent_name, pattern in INTENT_PATTERNS[:3]:  # add_user, remove_user, list_users
        if pattern.search(text):
            logger.debug(
                "Intent classified via rule",
                extra={"intent": intent_name},
            )
            return intent_name

    # Heuristic: PIN + passcode keyword = add_user (before arm/disarm)
    # Catches: "father-in-law ... passcode 1234" → add_user intent
    if ADD_USER_HEURISTIC.search(text):
        logger.debug(
            "Intent classified via heuristic",
            extra={"intent": "add_user"},
        )
        return "add_user"

    # Check remaining patterns (disarm, arm)
    for intent_name, pattern in INTENT_PATTERNS[3:]:  # disarm, arm
        if pattern.search(text):
            logger.debug(
                "Intent classified via rule",
                extra={"intent": intent_name},
            )
            return intent_name

    return None
