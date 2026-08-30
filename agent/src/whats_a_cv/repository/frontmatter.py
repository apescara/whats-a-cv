from typing import Any

import yaml


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return raw frontmatter and the untouched Markdown body."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None, text

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])

    raise ValueError("unclosed frontmatter")


def parse_frontmatter(
    text: str, source: str = "<string>"
) -> dict[str, Any]:
    raw, _ = split_frontmatter(text)
    if raw is None:
        return {}

    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise ValueError(f"{source}: invalid frontmatter YAML: {error}") from error

    if not isinstance(parsed, dict):
        raise ValueError(f"{source}: frontmatter must be a mapping")
    return parsed
