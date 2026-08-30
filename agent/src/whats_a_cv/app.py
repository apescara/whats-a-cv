from typing import Literal

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .repository import ProposalStore, RecordKind, RecordNotFoundError, list_records, load_record

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PROPOSALS = ProposalStore(REPOSITORY_ROOT / ".whats-a-cv" / "state.db")


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
        return load_record(REPOSITORY_ROOT, kind, slug)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


class ProposalRequest(BaseModel):
    target_path: str
    proposed_content: str


@app.post("/proposals")
def create_proposal(request: ProposalRequest):
    target = (REPOSITORY_ROOT / request.target_path).resolve()
    if not target.is_relative_to(REPOSITORY_ROOT) or target.suffix != ".md":
        raise HTTPException(status_code=422, detail="invalid target path")
    return {"id": PROPOSALS.create(target, request.proposed_content, REPOSITORY_ROOT)}


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
