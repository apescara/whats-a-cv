import os
from typing import Literal

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .repository import (
    ApplicationMetadata, ProposalStore, RecordKind, RecordNotFoundError,
    list_applications, list_records, load_record, read_application,
)
from .repository.service import related_expertise

def repository_root() -> Path:
    return Path(os.environ.get("WHATS_A_CV_REPOSITORY", Path(__file__).resolve().parents[3])).resolve()


REPOSITORY_ROOT = repository_root()
PROPOSALS = ProposalStore(REPOSITORY_ROOT / ".whats-a-cv" / "state.db", REPOSITORY_ROOT)


class HealthResponse(BaseModel):
    status: Literal["ok"]


app = FastAPI()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/records/{kind}")
def records(kind: RecordKind):
    return list_records(REPOSITORY_ROOT, kind)


@app.get("/records/{kind}/{slug}")
def record(kind: RecordKind, slug: str):
    try:
        loaded_record = load_record(REPOSITORY_ROOT, kind, slug)
        result = loaded_record.model_dump()
        result["related_expertise"] = related_expertise(REPOSITORY_ROOT, loaded_record)
        return result
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/applications")
def applications():
    return list_applications(REPOSITORY_ROOT)


@app.get("/applications/{slug}")
def application(slug: str):
    try:
        return read_application(REPOSITORY_ROOT, slug)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


class ProposalRequest(BaseModel):
    target_path: str
    proposed_content: str


@app.post("/proposals")
def create_proposal(request: ProposalRequest):
    target = Path(request.target_path)
    if target.is_absolute():
        raise HTTPException(status_code=422, detail="invalid target path")
    try:
        return {"id": PROPOSALS.create(target, request.proposed_content)}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/proposals/{proposal_id}")
def inspect_proposal(proposal_id: int):
    row = PROPOSALS.get(proposal_id)
    if row is None: raise HTTPException(status_code=404, detail="proposal not found")
    return dict(row)


@app.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: int):
    try: PROPOSALS.approve(proposal_id)
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error
    return inspect_proposal(proposal_id)


@app.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: int):
    try: PROPOSALS.reject(proposal_id)
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error
    return inspect_proposal(proposal_id)
