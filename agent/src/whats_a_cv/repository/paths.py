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


def proposal_path(root: Path, target: Path) -> Path:
    """Return a writable profile file, rejecting symlinks and other Markdown."""
    root = root.resolve()
    candidate = target if target.is_absolute() else root / target
    if candidate.is_symlink():
        raise ValueError("proposal target must not be a symlink")
    path = candidate.resolve()
    if path == root / "preferences.md":
        return path
    for kind in RecordKind:
        approved = (root / kind.value).resolve()
        if path.parent == approved and path.suffix == ".md":
            validate_slug(path.stem)
            return path
    raise ValueError("proposal target is not an approved profile file")
