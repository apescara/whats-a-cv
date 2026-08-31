from pathlib import Path

from whats_a_cv.repository import compile_latex
import whats_a_cv.repository.applications as applications


def test_compile_uses_rooted_working_directory_and_fixed_args(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "applications" / "role"
    path.mkdir(parents=True)
    (path / "cv.tex").write_text("\\documentclass{article}", encoding="utf-8")
    calls = {}

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def run(args, **kwargs):
        calls.update(args=args, kwargs=kwargs)
        return Result()

    monkeypatch.setattr(applications.subprocess, "run", run)
    result = compile_latex(tmp_path, "role")
    assert result["status"] == "ok"
    assert calls["args"] == ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "cv.tex"]
    assert calls["kwargs"]["cwd"] == path


def test_compile_reports_missing_latexmk(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "applications" / "role"
    path.mkdir(parents=True)
    (path / "cv.tex").write_text("\\documentclass{article}", encoding="utf-8")
    monkeypatch.setattr(applications.subprocess, "run", lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    assert compile_latex(tmp_path, "role") == {"status": "error", "error": "LaTeX compiler (latexmk) is not installed"}
