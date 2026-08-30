from pathlib import Path

from .frontmatter import serialize_frontmatter, split_frontmatter
from .records import Preferences


def read_preferences(path: Path) -> Preferences:
    return Preferences(body=split_frontmatter(path.read_text(encoding="utf-8"))[1] if path.exists() else "")


def serialize_preferences(preferences: Preferences) -> str:
    return serialize_frontmatter({}, preferences.body)
