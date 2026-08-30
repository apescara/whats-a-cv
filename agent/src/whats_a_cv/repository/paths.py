from pathlib import Path

from .kinds import RecordKind
from .slugs import validate_slug


def record_path(root: Path, kind: RecordKind | str, slug: str) -> Path:
    kind = RecordKind(kind)
    validate_slug(slug)
    approved = (root / kind.value).resolve()
    path = (approved / f"{slug}.md").resolve()
    if path.parent != approved or not path.is_relative_to(approved):
        raise ValueError("record path escapes its approved root")
    return path
