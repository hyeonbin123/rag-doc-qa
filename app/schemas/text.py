from typing import Annotated

from pydantic import AfterValidator


def reject_nul(value: str) -> str:
    # PostgreSQL text cannot hold U+0000. A value with it only fails when its row is written,
    # after the work the request asked for (for a question, the whole LLM answer), as a 500.
    if "\x00" in value:
        raise ValueError("must not contain the NUL character (U+0000)")
    return value


NulFreeStr = Annotated[str, AfterValidator(reject_nul)]
"""Request text the app stores in PostgreSQL."""
