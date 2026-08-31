from whats_a_cv.workflow import CheckpointStore, DraftBundle, ReviewDecision, continue_after_evidence, draft_requirements, evidence_review, finalize_application, ingest_job, model_settings, new_state, render_cv, render_job_post, retrieve_evidence, validate_artifacts
from whats_a_cv.app import WorkflowStartRequest, workflow_start
from whats_a_cv.repository import ApplicationMetadata


def test_evidence_review_survives_store_recreation(tmp_path):
    store = CheckpointStore(tmp_path / "state.db")
    state = new_state("stable-thread")
    state["evidence"] = {"candidates": []}
    evidence_review(state)
    store.save(state)

    recovered = CheckpointStore(tmp_path / "state.db").load("stable-thread")
    assert recovered is not None
    assert recovered["interrupt"] == "evidence_review"
    assert recovered["events"] == []


def test_workflow_start_keeps_unconfigured_ai_draft_usable(monkeypatch, tmp_path):
    monkeypatch.setattr("whats_a_cv.app.REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr("whats_a_cv.app.CHECKPOINTS", CheckpointStore(tmp_path / "state.db"))
    state = workflow_start(WorkflowStartRequest(text="Python data role", metadata=ApplicationMetadata(company="Acme", role="Engineer")))
    assert state["interrupt"] == "evidence_review"


def test_rendered_job_post_includes_original_description(tmp_path):
    state = new_state("job-post-thread")
    ingest_job(state, tmp_path, {"text": "Build reliable data pipelines.", "metadata": {"company": "Acme", "role": "Engineer"}})
    rendered = render_job_post(state)
    assert "Build reliable data pipelines." in rendered
    assert ".whats-a-cv/drafts" not in rendered


def test_retrieval_matches_canonical_expertise_and_experience_lines(tmp_path):
    (tmp_path / "expertise").mkdir()
    (tmp_path / "expertise" / "python.md").write_text('---\nname: Python\ncategory: language\n---\n\n# Python\n\n- Built data pipelines with Python.\n', encoding="utf-8")
    state = new_state("match-thread")
    state["requirements"] = draft_requirements("Required Python experience", tmp_path).model_dump()
    retrieve_evidence(state, tmp_path)
    candidates = state["evidence"]["candidates"]
    assert candidates and candidates[0]["source_path"] == "expertise/python.md"
    assert candidates[0]["confidence"] == 1


def test_retrieval_confidence_reflects_requirement_coverage(tmp_path):
    (tmp_path / "expertise").mkdir()
    (tmp_path / "expertise" / "python.md").write_text('---\nname: Python\ncategory: language\n---\n\n- Built Python SQL pipelines.\n', encoding="utf-8")
    state = new_state("coverage-thread")
    state["requirements"] = {"requirements": [{"id": "req-1", "category": "must-have", "text": "Python SQL AWS", "source_excerpt": "Python SQL AWS"}]}
    retrieve_evidence(state, tmp_path)
    assert state["evidence"]["candidates"][0]["confidence"] == 2 / 3


def test_approved_evidence_advances_to_a_draft():
    state = new_state("draft-thread")
    state["job"] = {"metadata": {"role": "Data Engineer"}}
    state["evidence"] = {"candidates": [{"requirement_id": "req-1", "source_path": "expertise/python.md", "excerpt": "Python", "relevance_reason": "match", "confidence": 1}]}
    evidence_review(state, ReviewDecision(action="approve", evidence_ids=["0"]))
    continue_after_evidence(state)
    assert state["stage"] == "generation_complete"
    assert state["drafts"]["cv"]["claims"][0]["evidence_ids"] == ["0"]


def test_validation_rejects_unresolved_cv_template_placeholders():
    state = new_state("placeholder-thread")
    state["job"] = {"metadata": {"language": "Spanish"}}
    files = {"job-post.md": "---\nlanguage: Spanish\n---\n", "cv.tex": "\\documentclass{article}\n\\address{CITY, COUNTRY}{}{}\n", "next-steps.mdx": "# Next steps\n"}
    assert "cv.tex contains unresolved template placeholders" in validate_artifacts(files, state)


def test_render_cv_uses_the_ai_document_when_supplied():
    state = new_state("ai-document-thread")
    state["drafts"] = {"cv": DraftBundle(summary="", cv_tex="\\documentclass{moderncv}\n\\begin{document}\n\\end{document}").model_dump()}
    assert render_cv(state, "ignored") == "\\documentclass{moderncv}\n\\begin{document}\n\\end{document}"


def test_task_model_overrides_the_default_provider_and_model(monkeypatch):
    monkeypatch.setenv("WHATS_A_CV_MODEL", "openai:gpt-5.6-luna")
    monkeypatch.setenv("WHATS_A_CV_CV_MODEL", "anthropic:claude-sonnet-4-5-20250929")
    settings = model_settings("cv")
    assert (settings.provider, settings.model) == ("anthropic", "claude-sonnet-4-5-20250929")


def test_finalize_reuses_stale_draft_directory_across_filesystems(monkeypatch, tmp_path):
    state = new_state("retry-thread")
    state["approvals"] = {"final": True}
    stale = tmp_path / ".whats-a-cv" / "drafts" / state["thread_id"]
    stale.mkdir(parents=True)
    files = {"job-post.md": "---\ncompany: Acme\nrole: Engineer\n---\n", "cv.tex": "\\documentclass{article}", "next-steps.mdx": "# Next steps\n"}
    monkeypatch.setattr("whats_a_cv.workflow.os.rename", lambda *_: (_ for _ in ()).throw(OSError(18, "Invalid cross-device link")))
    assert finalize_application(tmp_path, "2026-08-30-acme-engineer", files, state).is_dir()
    state["artifact_paths"] = ["applications/2026-08-30-acme-engineer/cv.tex"]
    assert finalize_application(tmp_path, "2026-08-30-acme-engineer", files, state).is_dir()
