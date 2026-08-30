from whats_a_cv.workflow import CheckpointStore, ReviewDecision, continue_after_evidence, draft_requirements, evidence_review, new_state, retrieve_evidence
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


def test_retrieval_matches_canonical_expertise_and_experience_lines(tmp_path):
    (tmp_path / "expertise").mkdir()
    (tmp_path / "expertise" / "python.md").write_text('---\nname: Python\ncategory: language\n---\n\n# Python\n\n- Built data pipelines with Python.\n', encoding="utf-8")
    state = new_state("match-thread")
    state["requirements"] = draft_requirements("Required Python experience", tmp_path).model_dump()
    retrieve_evidence(state, tmp_path)
    candidates = state["evidence"]["candidates"]
    assert candidates and candidates[0]["source_path"] == "expertise/python.md"


def test_approved_evidence_advances_to_a_draft():
    state = new_state("draft-thread")
    state["job"] = {"metadata": {"role": "Data Engineer"}}
    state["evidence"] = {"candidates": [{"requirement_id": "req-1", "source_path": "expertise/python.md", "excerpt": "Python", "relevance_reason": "match", "confidence": 1}]}
    evidence_review(state, ReviewDecision(action="approve", evidence_ids=["0"]))
    continue_after_evidence(state)
    assert state["stage"] == "generation_complete"
    assert state["drafts"]["cv"]["claims"][0]["evidence_ids"] == ["0"]
