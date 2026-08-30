import re


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(slug: str) -> str:
    if slug == "_template" or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"invalid record slug: {slug!r}")
    return slug
