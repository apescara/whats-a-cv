def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return raw frontmatter and the untouched Markdown body."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None, text

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])

    raise ValueError("unclosed frontmatter")
