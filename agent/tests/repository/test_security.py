from pathlib import Path
from threading import Event, Thread

import pytest

from whats_a_cv.repository import ProposalStore, RecordKind, atomic_write, list_records, load_record, proposal_path
import whats_a_cv.repository.proposals as proposals


def profile_root(tmp_path: Path) -> Path:
    for kind in RecordKind:
        (tmp_path / kind.value).mkdir()
    return tmp_path


def test_proposals_only_target_profile_records(tmp_path: Path) -> None:
    root = profile_root(tmp_path)
    store = ProposalStore(tmp_path / "state.db", root)
    (root / "README.md").write_text("private notes\n")

    with pytest.raises(ValueError, match="approved profile"):
        store.create(Path("README.md"), "changed\n")
    with pytest.raises(ValueError, match="invalid record slug"):
        proposal_path(root, Path("experience/_template.md"))


def test_proposals_reject_symlink_targets(tmp_path: Path) -> None:
    root = profile_root(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("private\n")
    target = root / "experience" / "role.md"
    target.symlink_to(outside)

    with pytest.raises(ValueError, match="symlink"):
        ProposalStore(tmp_path / "state.db", root).create(target, "changed\n")
    with pytest.raises(ValueError, match="symlink"):
        atomic_write(target, "changed\n")


def test_only_one_concurrent_approval_can_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = profile_root(tmp_path)
    target = root / "experience" / "role.md"
    target.write_text("old\n")
    store = ProposalStore(tmp_path / "state.db", root)
    proposal_id = store.create(target, "new\n")
    wrote, release = Event(), Event()
    original_write = proposals.atomic_write

    def delayed_write(path: Path, content: str) -> None:
        original_write(path, content)
        wrote.set()
        release.wait(timeout=2)

    monkeypatch.setattr(proposals, "atomic_write", delayed_write)
    first = Thread(target=store.approve, args=(proposal_id,))
    first.start()
    assert wrote.wait(timeout=2)
    errors: list[Exception] = []

    def approve_again() -> None:
        try:
            ProposalStore(tmp_path / "state.db", root).approve(proposal_id)
        except ValueError as error:
            errors.append(error)

    second = Thread(target=approve_again)
    second.start()
    release.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert target.read_text() == "new\n"
    assert [str(error) for error in errors] == ["proposal is not pending"]


def test_invalid_contact_errors_do_not_expose_its_value(tmp_path: Path) -> None:
    root = profile_root(tmp_path)
    secret = "candidate@example.test"
    (root / "contact" / "primary.md").write_text(
        f"---\ntype: invalid\nvalue: {secret}\n---\n"
    )

    summary = list_records(root, RecordKind.CONTACT)[0]

    assert summary.error == "invalid contact record"
    assert secret not in str(summary)
    with pytest.raises(ValueError, match="invalid contact record") as error:
        load_record(root, RecordKind.CONTACT, "primary")
    assert secret not in str(error.value)
