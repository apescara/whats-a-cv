from whats_a_cv.app import app, health


def test_health() -> None:
    assert health().model_dump() == {"status": "ok"}
    assert any(
        route.path == "/health" and "GET" in route.methods
        for route in app.routes
    )
