import difflib
from pathlib import Path


def unified_diff(path: Path, old: str, new: str, *, relative_to: Path | None = None) -> str:
    name = str(path if relative_to is None else path.relative_to(relative_to))
    return "".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=name, tofile=name,
    ))
