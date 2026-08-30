from pathlib import Path

from .repository import ProposalStore, RecordKind, list_records, load_record


TOOLS = {"list_records": list_records, "read_record": load_record, "create_proposal": ProposalStore.create, "get_proposal": ProposalStore.get}


def manifest() -> dict:
    return {"name": "whats-a-cv", "tools": sorted(TOOLS)}


def list_records_tool(root: Path, kind: RecordKind | str):
    return list_records(root, kind)


def read_record_tool(root: Path, kind: RecordKind | str, slug: str):
    return load_record(root, kind, slug)
