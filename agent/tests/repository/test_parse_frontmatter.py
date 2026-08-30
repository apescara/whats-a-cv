import pytest

from whats_a_cv.repository import parse_frontmatter


def test_parse_frontmatter_returns_mapping() -> None:
    assert parse_frontmatter('---\ntitle: Example\ncount: 2\n---\n') == {
        "title": "Example",
        "count": 2,
    }


def test_parse_frontmatter_rejects_non_mapping() -> None:
    with pytest.raises(ValueError, match="profile.md: frontmatter must be a mapping"):
        parse_frontmatter("---\n- item\n---\n", "profile.md")


def test_parse_frontmatter_includes_file_context_for_invalid_yaml() -> None:
    with pytest.raises(ValueError, match="profile.md: invalid frontmatter YAML"):
        parse_frontmatter("---\ntitle: [\n---\n", "profile.md")
