from pathlib import Path

from whats_a_cv.repository import ProposalStore, application_metadata_proposal, read_application


def test_status_proposal_is_separate_from_generated_artifacts(tmp_path: Path) -> None:
    path = tmp_path / "applications" / "example-role"
    path.mkdir(parents=True)
    (path / "job-post.md").write_text("---\ncompany: Acme\nrole: Engineer\n---\n", encoding="utf-8")
    (path / "cv.tex").write_text("generated", encoding="utf-8")
    store = ProposalStore(tmp_path / "state.db", tmp_path)

    proposal = application_metadata_proposal(store, tmp_path, "example-role", "status.md", "interview")

    assert not (path / "status.md").exists()
    assert (path / "cv.tex").read_text() == "generated"
    store.approve(proposal)
    assert read_application(tmp_path, "example-role").metadata.status == "interview"
