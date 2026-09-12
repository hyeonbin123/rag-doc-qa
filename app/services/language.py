"""Question language detection, used to pick which docs translation to search."""

import re
from typing import Literal

Language = Literal["en", "ko"]
SUPPORTED_LANGUAGES: tuple[Language, ...] = ("en", "ko")

_HANGUL_RE = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")


def detect_language(text: str) -> Language:
    """Korean if the text contains any Hangul, otherwise English.

    Korean questions usually mix in English API names ("HTTPException으로 404를
    반환하려면?"), so a single Hangul character is enough to call it Korean.
    """
    return "ko" if _HANGUL_RE.search(text) else "en"
