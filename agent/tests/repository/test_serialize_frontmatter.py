from whats_a_cv.repository import serialize_frontmatter


def test_serialize_frontmatter_snapshot() -> None:
    assert serialize_frontmatter(
        {"title": "Example", "count": 2}, "# Example"
    ) == "---\ntitle: Example\ncount: 2\n---\n# Example\n"


def test_serialize_frontmatter_preserves_existing_body_newline() -> None:
    assert serialize_frontmatter({}, "Body\n") == "---\n{}\n---\nBody\n"
