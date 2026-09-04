import os
import json
import re
from datetime import date
from typing import Literal

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from .repository import (
    ApplicationMetadata, ProposalStore, RecordKind, RecordNotFoundError,
    list_applications, list_records, load_record, read_application,
    read_artifact, application_metadata_proposal,
    JobDraft, fetch_job_url, compile_latex, delete_draft_application,
)
from .repository.service import related_experience, related_expertise
from .workflow import (CheckpointStore, DraftBundle, EvidenceSet, ModelSettings, NextSteps, RequirementSet, ReviewDecision,
                       ai_fallback_warning, continue_after_evidence, draft_cv, draft_next_steps, draft_requirements, evidence_review,
                       extract_requirements, finalize_application, ingest_job, new_state, checkpoint_store,
                       profile_context, rank_evidence, render_cv_source, render_job_post, render_next_steps_file,
                       retrieve_evidence, structured_model, workflow_event, model_settings)

MODEL_ENV_KEYS = {
    "default": "WHATS_A_CV_MODEL",
    "requirements": "WHATS_A_CV_REQUIREMENTS_MODEL",
    "evidence": "WHATS_A_CV_EVIDENCE_MODEL",
    "cv": "WHATS_A_CV_CV_MODEL",
    "next_steps": "WHATS_A_CV_NEXT_STEPS_MODEL",
}
API_KEY_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}
DEFAULT_MODEL = "openai:gpt-5.6-luna"
RUNTIME_API_KEYS: dict[str, str] = {}
RUNTIME_MODELS: dict[str, str] = {}

def repository_root() -> Path:
    return Path(os.environ.get("WHATS_A_CV_REPOSITORY", Path(__file__).resolve().parents[3])).resolve()


REPOSITORY_ROOT = repository_root()
PROPOSALS = ProposalStore(REPOSITORY_ROOT / ".whats-a-cv" / "state.db", REPOSITORY_ROOT)
CHECKPOINTS = checkpoint_store(REPOSITORY_ROOT)


class HealthResponse(BaseModel):
    status: Literal["ok"]


app = FastAPI()


def ai_enabled() -> bool:
    return bool(RUNTIME_API_KEYS) or any(os.getenv(name) for name in API_KEY_ENV_KEYS.values())


def validate_model(value: str) -> None:
    provider, separator, model = value.partition(":")
    if not separator or not provider or not model:
        raise ValueError("models must use provider:model, for example openai:gpt-5.6-luna")
    if provider not in {"openai", "anthropic", "google"}:
        raise ValueError("model provider must be openai, anthropic, or google")


def active_model_settings(task: str) -> ModelSettings:
    settings = model_settings(task)
    configured = RUNTIME_MODELS.get(task)
    if not configured and task != "default":
        configured = os.getenv(MODEL_ENV_KEYS[task])
    configured = configured or RUNTIME_MODELS.get("default")
    if configured:
        provider, _, model = configured.partition(":")
        settings = settings.model_copy(update={"provider": provider, "model": model})
    if api_key := RUNTIME_API_KEYS.get(settings.provider):
        settings = settings.model_copy(update={"api_key": api_key})
    return settings


class SettingsUpdate(BaseModel):
    api_keys: dict[str, str] = {}
    models: dict[str, str] = {}


def settings_summary() -> dict:
    return {
        "keys": {name: bool(RUNTIME_API_KEYS.get(name) or os.getenv(env_key)) for name, env_key in API_KEY_ENV_KEYS.items()},
        "models": {
            name: RUNTIME_MODELS.get(name, os.getenv(env_key, DEFAULT_MODEL if name == "default" else ""))
            for name, env_key in MODEL_ENV_KEYS.items()
        },
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/settings")
def settings():
    return settings_summary()


@app.put("/settings")
def update_settings(request: SettingsUpdate):
    unknown = set(request.api_keys) - set(API_KEY_ENV_KEYS)
    unknown |= set(request.models) - set(MODEL_ENV_KEYS)
    if unknown:
        raise HTTPException(status_code=422, detail=f"unsupported setting: {sorted(unknown)[0]}")
    if any(not value.strip() for value in request.api_keys.values()):
        raise HTTPException(status_code=422, detail="API keys cannot be empty")
    if any(name == "default" and not value.strip() for name, value in request.models.items()):
        raise HTTPException(status_code=422, detail="the default model is required")
    try:
        for value in request.models.values():
            if value.strip():
                validate_model(value.strip())
        RUNTIME_API_KEYS.update({name: value.strip() for name, value in request.api_keys.items()})
        for name, value in request.models.items():
            if value.strip():
                RUNTIME_MODELS[name] = value.strip()
            else:
                RUNTIME_MODELS.pop(name, None)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {**settings_summary(), "runtime_only": True}


@app.get("/records/{kind}")
def records(kind: RecordKind):
    return list_records(REPOSITORY_ROOT, kind)


@app.get("/records/{kind}/{slug}")
def record(kind: RecordKind, slug: str):
    try:
        loaded_record = load_record(REPOSITORY_ROOT, kind, slug)
        result = loaded_record.model_dump()
        result["related_expertise"] = related_expertise(REPOSITORY_ROOT, loaded_record)
        if kind is RecordKind.EXPERTISE:
            result["related_experience"] = related_experience(REPOSITORY_ROOT, loaded_record)
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


@app.delete("/applications/{slug}", status_code=204)
def delete_application(slug: str):
    try:
        delete_draft_application(REPOSITORY_ROOT, slug)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


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


class WorkflowStartRequest(BaseModel):
    text: str
    metadata: ApplicationMetadata
    thread_id: str | None = None


@app.post("/workflow/start")
def workflow_start(request: WorkflowStartRequest):
    state = new_state(request.thread_id)
    ingest_job(state, REPOSITORY_ROOT, {"text": request.text, "metadata": request.metadata.model_dump()})
    used_ai = False
    if ai_enabled():
        try:
            extract_requirements(state, structured_model(RequirementSet, settings=active_model_settings("requirements")))
            used_ai = True
        except Exception as error:
            state["warnings"] = [ai_fallback_warning(error)]
            state["ai_fallback"] = True
    if not used_ai:
        state["requirements"] = draft_requirements(request.text, REPOSITORY_ROOT).model_dump()
    retrieve_evidence(state, REPOSITORY_ROOT)
    if used_ai:
        try:
            rank_evidence(state, structured_model(EvidenceSet, settings=active_model_settings("evidence")))
        except Exception as error:
            state["warnings"] = [ai_fallback_warning(error)]
            state["ai_fallback"] = True
    state["interrupt"] = "evidence_review"
    workflow_event(state, "evidence_review", "waiting")
    CHECKPOINTS.save(state)
    return state


@app.get("/workflow/{thread_id}")
def workflow_inspect(thread_id: str):
    state = CHECKPOINTS.load(thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    return state


class WorkflowResumeRequest(BaseModel):
    decision: ReviewDecision | None = None


@app.post("/workflow/{thread_id}/resume")
def workflow_resume(thread_id: str, request: WorkflowResumeRequest):
    state = CHECKPOINTS.load(thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    if state.get("interrupt") == "evidence_review":
        evidence_review(state, request.decision)
        if request.decision and request.decision.action == "approve":
            if ai_enabled() and not state.get("ai_fallback"):
                try:
                    draft_cv(state, structured_model(DraftBundle, settings=active_model_settings("cv")), profile_context(REPOSITORY_ROOT))
                    draft_next_steps(state, structured_model(NextSteps, settings=active_model_settings("next_steps")))
                    state["stage"] = "generation_complete"
                    workflow_event(state, "draft_cv")
                except Exception as error:
                    state["warnings"] = [ai_fallback_warning(error)]
                    state["ai_fallback"] = True
                    continue_after_evidence(state)
            else:
                continue_after_evidence(state)
    CHECKPOINTS.save(state)
    return state


@app.post("/workflow/{thread_id}/finalize")
def workflow_finalize(thread_id: str):
    state = CHECKPOINTS.load(thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    state["approvals"] = {"final": True}
    metadata = state["job"]["metadata"]
    slug = re.sub(r"[^a-z0-9]+", "-", f"{metadata.get('date') or date.today().isoformat()}-{metadata['company']}-{metadata['role']}".lower()).strip("-")
    files = {
        "job-post.md": render_job_post(state),
        "cv.tex": render_cv_source(state, REPOSITORY_ROOT / "TEMPLATE.tex"),
        "next-steps.mdx": render_next_steps_file(state),
    }
    try:
        path = finalize_application(REPOSITORY_ROOT, slug, files, state)
    except (FileExistsError, ValueError, OSError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    CHECKPOINTS.save(state)
    return {"slug": slug, "path": str(path.relative_to(REPOSITORY_ROOT))}


@app.get("/workflow/{thread_id}/events")
def workflow_events(thread_id: str):
    state = CHECKPOINTS.load(thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    body = "".join(f"data: {json.dumps(event)}\n\n" for event in state.get("events", []))
    return StreamingResponse(iter([body]), media_type="text/event-stream")


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
