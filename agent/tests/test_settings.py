from whats_a_cv import app as app_module


def test_settings_apply_keys_and_models_for_the_current_session(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(app_module, "RUNTIME_API_KEYS", {})
    monkeypatch.setattr(app_module, "RUNTIME_MODELS", {})

    saved = app_module.update_settings(app_module.SettingsUpdate(
        api_keys={"openai": "secret-key"},
        models={"default": "openai:runtime-model", "cv": "anthropic:claude-sonnet-4-5-20250929"},
    ))

    assert saved["keys"]["openai"] is True
    assert "secret-key" not in str(saved)
    assert saved["models"]["cv"] == "anthropic:claude-sonnet-4-5-20250929"
    assert not (tmp_path / ".env").exists()
    settings = app_module.active_model_settings("cv")
    assert (settings.provider, settings.model, settings.api_key) == ("anthropic", "claude-sonnet-4-5-20250929", None)
    default = app_module.active_model_settings("requirements")
    assert (default.provider, default.model, default.api_key) == ("openai", "runtime-model", "secret-key")


def test_settings_reject_unknown_or_invalid_models(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(app_module, "RUNTIME_API_KEYS", {})
    monkeypatch.setattr(app_module, "RUNTIME_MODELS", {})

    try:
        app_module.update_settings(app_module.SettingsUpdate(models={"cv": "not-a-model"}))
    except app_module.HTTPException as error:
        assert error.status_code == 422
    else:
        raise AssertionError("invalid model was accepted")
