import pytest

from whats_a_cv.repository import split_frontmatter


def test_split_frontmatter_returns_raw_header_and_body() -> None:
    header, body = split_frontmatter("---\ntitle: Example\n---\n# ---\nBody\n")

    assert header == "title: Example\n"
    assert body == "# ---\nBody\n"


def test_split_frontmatter_handles_missing_header() -> None:
    text = "# Example\n\nBody\n"

    assert split_frontmatter(text) == (None, text)


def test_split_frontmatter_rejects_unclosed_header() -> None:
    with pytest.raises(ValueError, match="unclosed frontmatter"):
        split_frontmatter("---\ntitle: Example\n")
