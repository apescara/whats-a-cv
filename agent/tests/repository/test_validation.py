from pathlib import Path

import pytest

from whats_a_cv.repository import atomic_write, record_path, unified_diff, validate_date, validate_slug
from whats_a_cv.repository import RecordKind


@pytest.mark.parametrize("slug", ["good-record", "a1", "a-b2"])
def test_valid_slugs(slug: str) -> None:
    assert validate_slug(slug) == slug


@pytest.mark.parametrize("slug", ["Bad", "../escape", "_template", "a_b", ""])
def test_invalid_slugs(slug: str) -> None:
    with pytest.raises(ValueError):
        validate_slug(slug)


def test_dates() -> None:
    assert validate_date("2026-08") == "2026-08"
    assert validate_date("2026-08-30") == "2026-08-30"
    assert validate_date("present", allow_present=True) == "present"
    with pytest.raises(ValueError):
        validate_date("2026-02-30")


def test_record_path_is_rooted(tmp_path: Path) -> None:
    assert record_path(tmp_path, RecordKind.EXPERIENCE, "role.md"[:-3]).name == "role.md"
    with pytest.raises(ValueError):
        record_path(tmp_path, RecordKind.EXPERIENCE, "../escape")


def test_atomic_write_and_diff(tmp_path: Path) -> None:
    path = tmp_path / "experience" / "role.md"
    atomic_write(path, "old\n")
    assert path.read_text() == "old\n"
    assert unified_diff(path, "old\n", "new\n", relative_to=tmp_path).startswith("--- experience/role.md")
