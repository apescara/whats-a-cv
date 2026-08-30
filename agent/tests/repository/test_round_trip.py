from pathlib import Path

from whats_a_cv.repository import parse_frontmatter, serialize_frontmatter, split_frontmatter


ROOT = Path(__file__).parents[3]
RECORD_ROOTS = (
    "contact",
    "experience",
    "education",
    "certifications",
    "projects",
    "expertise",
    "languages",
)


def test_tracked_records_round_trip_semantically() -> None:
    paths = [
        path
        for root in RECORD_ROOTS
        for path in sorted((ROOT / root).glob("*.md"))
        if path.name != "_template.md"
    ]

    assert paths
    for path in paths:
        text = path.read_text()
        frontmatter, body = split_frontmatter(text)
        assert frontmatter is not None
        result = serialize_frontmatter(parse_frontmatter(text, str(path)), body)
        assert parse_frontmatter(result, str(path)) == parse_frontmatter(text, str(path))
        assert split_frontmatter(result)[1] == body
