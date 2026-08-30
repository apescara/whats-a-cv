from datetime import date
import re


def validate_date(value: str, *, allow_present: bool = False, allow_blank: bool = False) -> str:
    if allow_blank and value == "":
        return value
    if allow_present and value == "present":
        return value
    if not re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", value):
        raise ValueError(f"invalid ISO date: {value!r}")
    try:
        date.fromisoformat(value if len(value) == 10 else f"{value}-01")
    except ValueError as error:
        raise ValueError(f"invalid ISO date: {value!r}") from error
    return value
