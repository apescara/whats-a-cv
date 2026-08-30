from whats_a_cv.app import app, health, repository_root


def test_health() -> None:
    assert health().model_dump() == {"status": "ok"}
    assert any(
        route.path == "/health" and "GET" in route.methods
        for route in app.routes
    )


def test_repository_root_uses_runtime_setting(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("WHATS_A_CV_REPOSITORY", str(tmp_path))

    assert repository_root() == tmp_path
