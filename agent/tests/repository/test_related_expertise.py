from pathlib import Path

from whats_a_cv.repository import RecordKind, load_record
from whats_a_cv.repository.service import related_expertise, sort_date


def test_related_expertise_uses_only_the_skills_section(tmp_path: Path) -> None:
    (tmp_path / "experience").mkdir()
    (tmp_path / "expertise").mkdir()
    (tmp_path / "experience" / "role.md").write_text(
        '---\ncompany: "Acme"\nrole: "Engineer"\nstart: "2025-01"\nend: "present"\n---\n\n## Skills\n\n- Python\n',
        encoding="utf-8",
    )
    (tmp_path / "expertise" / "python.md").write_text(
        '---\nname: "Python"\ncategory: "language"\n---\n', encoding="utf-8"
    )
    (tmp_path / "expertise" / "sql.md").write_text(
        '---\nname: "SQL"\ncategory: "language"\n---\nPython is not a SQL reference.\n', encoding="utf-8"
    )

    record = load_record(tmp_path, RecordKind.EXPERIENCE, "role")

    assert related_expertise(tmp_path, record) == [{"slug": "python", "name": "Python"}]


def test_sort_date_normalizes_supported_record_dates() -> None:
    assert sort_date("present") == "9999-12-31"
    assert sort_date("2025-07") == "2025-07-01"
    assert sort_date("Oct 2025") == "2025-10-01"
