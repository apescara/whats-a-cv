from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from whats_a_cv.repository import (
    ApplicationMetadata, delete_draft_application, list_applications, normalize_job_html, read_application,
)


def make_application(root: Path, *, legacy: bool = True) -> Path:
    path = root / "applications" / "2026-08-27-option-data-engineer"
    path.mkdir(parents=True)
    (path / "job-post.md").write_text(
        '---\ncompany: Option\nrole: Data Engineer\nlocation: LATAM\n'
        'date: 2026-08-27\nlanguage: es\nsource_url: https://example.test\n'
        'retrieved: 2026-08-27\nstatus: drafting\n---\n# Job\n', encoding="utf-8"
    )
    if legacy:
        (path / "next-steps.md").write_text("# Next steps\n", encoding="utf-8")
    return path


def test_application_metadata_and_existing_bundle_round_trip(tmp_path: Path) -> None:
    path = make_application(tmp_path)
    (path / "cv.tex").write_text("\\documentclass{article}", encoding="utf-8")
    bundle = read_application(tmp_path, path.name)

    assert ApplicationMetadata.model_validate(bundle.metadata.model_dump()) == bundle.metadata
    assert bundle.metadata.company == "Option"
    assert bundle.metadata.artifacts.next_steps == "next-steps.md"
    assert list_applications(tmp_path)[0].has_pdf is False


def test_application_bundle_reports_extra_files(tmp_path: Path) -> None:
    path = make_application(tmp_path)
    (path / "unexpected.txt").write_text("not an artifact", encoding="utf-8")

    assert read_application(tmp_path, path.name).extra_files == ["unexpected.txt"]


def test_missing_application_and_invalid_slug_are_safe(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_application(tmp_path, "missing")
    with pytest.raises(ValueError):
        read_application(tmp_path, "../outside")


def test_legacy_next_steps_fallback_and_mdx_preference(tmp_path: Path) -> None:
    path = make_application(tmp_path)
    assert read_application(tmp_path, path.name).metadata.artifacts.next_steps == "next-steps.md"
    (path / "next-steps.mdx").write_text("# Canonical\n", encoding="utf-8")
    assert read_application(tmp_path, path.name).metadata.artifacts.next_steps == "next-steps.mdx"


def test_only_draft_applications_can_be_deleted(tmp_path: Path) -> None:
    path = make_application(tmp_path)
    delete_draft_application(tmp_path, path.name)
    assert not path.exists()

    path = make_application(tmp_path)
    job_post = path / "job-post.md"
    job_post.write_text(job_post.read_text(encoding="utf-8").replace("status: drafting", "status: submitted"), encoding="utf-8")
    with pytest.raises(ValueError, match="only draft"):
        delete_draft_application(tmp_path, path.name)


def test_hostile_html_is_inert_text() -> None:
    assert "<script" not in normalize_job_html('<h1>Role</h1><script>alert(1)</script>Text')


def test_public_url_fetch_rejects_localhost() -> None:
    from whats_a_cv.repository.applications import fetch_job_url
    with pytest.raises(ValueError, match="private network"):
        fetch_job_url("http://127.0.0.1/job")


def test_public_url_fetch_rechecks_redirect_targets(monkeypatch) -> None:
    from whats_a_cv.repository import applications

    class Opener:
        def open(self, request: Request, timeout: float):
            raise HTTPError(request.full_url, 302, "Found", {"Location": "http://127.0.0.1/private"}, BytesIO())

    monkeypatch.setattr(applications, "build_opener", lambda _handler: Opener())
    monkeypatch.setattr(applications, "_public_host", lambda host: host != "127.0.0.1")
    with pytest.raises(ValueError, match="private network"):
        applications.fetch_job_url("https://public.example/job")
