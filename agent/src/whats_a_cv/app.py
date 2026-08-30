import os
from datetime import date
from typing import Literal

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from .repository import (
    ApplicationMetadata, ProposalStore, RecordKind, RecordNotFoundError,
    list_applications, list_records, load_record, read_application,
    read_artifact, application_metadata_proposal,
    JobDraft, fetch_job_url, compile_latex,
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
def application(slug: str, include_notes: bool = False):
    try:
        return read_application(REPOSITORY_ROOT, slug, include_notes=include_notes)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


COMPILE_RESULTS: dict[str, dict] = {}


@app.post("/applications/{slug}/compile")
def compile_application(slug: str):
    try:
        result = compile_latex(REPOSITORY_ROOT, slug)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    COMPILE_RESULTS[slug] = result
    return result


@app.get("/applications/{slug}/compile")
def compilation_status(slug: str):
    return COMPILE_RESULTS.get(slug, {"status": "not_started"})


@app.get("/applications/{slug}/{filename}")
def application_artifact(slug: str, filename: str):
    try:
        path, content = read_artifact(REPOSITORY_ROOT, slug, filename)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    media_type = "application/pdf" if path.suffix == ".pdf" else "text/plain; charset=utf-8"
    return Response(content, media_type=media_type, headers={"Content-Disposition": f'inline; filename="{path.name}"'})


class ApplicationStatusRequest(BaseModel):
    status: str


@app.post("/applications/{slug}/status")
def propose_application_status(slug: str, request: ApplicationStatusRequest):
    try:
        return {"id": application_metadata_proposal(PROPOSALS, REPOSITORY_ROOT, slug, "status.md", request.status)}
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


class ApplicationNotesRequest(BaseModel):
    notes: str


@app.post("/applications/{slug}/notes")
def propose_application_notes(slug: str, request: ApplicationNotesRequest):
    try:
        return {"id": application_metadata_proposal(PROPOSALS, REPOSITORY_ROOT, slug, "notes.md", request.notes)}
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


class JobDraftRequest(BaseModel):
    text: str
    metadata: ApplicationMetadata


@app.post("/job-draft")
def save_job_draft(request: JobDraftRequest):
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="job text is required")
    return JobDraft(text=request.text, metadata=request.metadata, source_url=request.metadata.source_url, retrieved=request.metadata.retrieved)


class JobUrlRequest(BaseModel):
    url: str


@app.post("/job-url")
def fetch_job(request: JobUrlRequest):
    try:
        text, url = fetch_job_url(request.url)
        return {"text": text, "source_url": url, "retrieved": date.today().isoformat()}
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
