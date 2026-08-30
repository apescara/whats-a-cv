"""Small, typed LangGraph application workflow primitives."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .repository import ApplicationMetadata, RecordKind, atomic_write, list_records, load_record

RequirementCategory = Literal["must-have", "preferred", "responsibility", "keyword", "recruiter-concern"]


class ModelSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = "gpt-5.6-luna"
    review_model: str | None = None
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"] = "medium"
    api_key: str | None = None

    @field_validator("model")
    @classmethod
    def supported_model(cls, value: str) -> str:
        if value not in {"gpt-5.6-luna", "gpt-5.6-terra"}:
            raise ValueError("model must be gpt-5.6-luna or gpt-5.6-terra")
        return value

    def require_key(self) -> str:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("AI actions require OPENAI_API_KEY")
        return key


def model_settings() -> ModelSettings:
    return ModelSettings(
        model=os.getenv("WHATS_A_CV_MODEL", "gpt-5.6-luna"),
        review_model=os.getenv("WHATS_A_CV_REVIEW_MODEL") or None,
        reasoning_effort=os.getenv("WHATS_A_CV_REASONING_EFFORT", "medium"),
    )


def model_factory(settings: ModelSettings | None = None):
    from langchain_openai import ChatOpenAI
    settings = settings or model_settings()
    return ChatOpenAI(model=settings.model, api_key=settings.require_key(), reasoning_effort=settings.reasoning_effort)


def structured_model(schema: type[BaseModel], settings: ModelSettings | None = None):
    return model_factory(settings).with_structured_output(schema)


def stream_model(settings: ModelSettings | None = None):
    return model_factory(settings).astream


class Requirement(BaseModel):
    id: str
    category: RequirementCategory
    text: str
    source_excerpt: str


class RequirementSet(BaseModel):
    requirements: list[Requirement]

    @field_validator("requirements")
    @classmethod
    def unique_ids(cls, value: list[Requirement]) -> list[Requirement]:
        if len({item.id for item in value}) != len(value):
            raise ValueError("requirement IDs must be unique")
        return value


class EvidenceCandidate(BaseModel):
    requirement_id: str
    source_path: str
    section: str = ""
    excerpt: str
    relevance_reason: str
    confidence: float = Field(ge=0, le=1)

    @field_validator("source_path", "excerpt")
    @classmethod
    def required_source_reference(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("evidence requires a source reference and excerpt")
        return value


class EvidenceSet(BaseModel):
    candidates: list[EvidenceCandidate]


class ReviewDecision(BaseModel):
    action: Literal["approve", "replace", "reject"]
    evidence_ids: list[str] = Field(default_factory=list)
    notes: str = ""


class DraftClaim(BaseModel):
    text: str
    evidence_ids: list[str] = Field(min_length=1)


class DraftBundle(BaseModel):
    summary: str
    claims: list[DraftClaim] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class CompilationState(BaseModel):
    status: Literal["not_started", "ok", "error"] = "not_started"
    pages: int | None = None
    errors: list[str] = Field(default_factory=list)


class GraphState(TypedDict, total=False):
    thread_id: str
    job: dict[str, Any]
    requirements: dict[str, Any]
    evidence: dict[str, Any]
    decisions: dict[str, Any]
    drafts: dict[str, Any]
    validation: dict[str, Any]
    compilation: dict[str, Any]
    approvals: dict[str, Any]
    artifact_paths: list[str]
    events: list[dict[str, Any]]
    interrupt: str | None


def new_state(thread_id: str | None = None) -> GraphState:
    return {"thread_id": thread_id or str(uuid.uuid4()), "events": [], "interrupt": None}


def state_json(state: GraphState) -> str:
    return json.dumps(state, sort_keys=True)


def state_from_json(value: str) -> GraphState:
    state = json.loads(value)
    if not isinstance(state, dict) or not state.get("thread_id"):
        raise ValueError("invalid graph state")
    return state


class CheckpointStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS checkpoints (thread_id TEXT PRIMARY KEY, state TEXT NOT NULL)")

    def save(self, state: GraphState) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO checkpoints VALUES (?, ?)", (state["thread_id"], state_json(state)))

    def load(self, thread_id: str) -> GraphState | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT state FROM checkpoints WHERE thread_id = ?", (thread_id,)).fetchone()
        return state_from_json(row[0]) if row else None


def checkpoint_store(root: Path) -> CheckpointStore:
    return CheckpointStore(root / ".whats-a-cv" / "state.db")


def ingest_job(state: GraphState, root: Path, job: dict[str, Any]) -> GraphState:
    metadata = ApplicationMetadata.model_validate(job.get("metadata", job))
    text = str(job.get("text", "")).strip()
    if not text:
        raise ValueError("job text is required")
    path = root / ".whats-a-cv" / "jobs" / f"{state['thread_id']}.md"
    atomic_write(path, text + "\n")
    state["job"] = {"metadata": metadata.model_dump(), "source_path": str(path.relative_to(root))}
    return state


def extract_requirements(state: GraphState, model: Any) -> GraphState:
    prompt = state["job"]
    result = model.invoke(json.dumps(prompt))
    result = result if isinstance(result, RequirementSet) else RequirementSet.model_validate(result)
    state["requirements"] = result.model_dump()
    return state


def retrieve_evidence(state: GraphState, root: Path) -> GraphState:
    requirements = RequirementSet.model_validate(state["requirements"])
    candidates: list[EvidenceCandidate] = []
    for requirement in requirements.requirements:
        terms = {word.lower() for word in requirement.text.split() if len(word) > 2}
        for kind in RecordKind:
            for summary in list_records(root, kind):
                if not summary.valid:
                    continue
                record = load_record(root, kind, summary.slug)
                for line in record.body.splitlines():
                    if terms and len(terms & set(line.lower().split())) >= max(1, min(2, len(terms))):
                        candidates.append(EvidenceCandidate(requirement_id=requirement.id, source_path=summary.relative_path, section="body", excerpt=line.strip(), relevance_reason="lexical match", confidence=0.5))
    state["evidence"] = EvidenceSet(candidates=candidates).model_dump()
    return state


def rank_evidence(state: GraphState, model: Any) -> GraphState:
    supplied = EvidenceSet.model_validate(state.get("evidence", {}))
    result = model.invoke(supplied.model_dump_json())
    ranked = result if isinstance(result, EvidenceSet) else EvidenceSet.model_validate(result)
    allowed = {(item.requirement_id, item.source_path, item.excerpt) for item in supplied.candidates}
    if any((item.requirement_id, item.source_path, item.excerpt) not in allowed for item in ranked.candidates):
        raise ValueError("model returned evidence that was not supplied")
    state["evidence"] = ranked.model_dump()
    return state


def evidence_review(state: GraphState, decision: ReviewDecision | None = None) -> GraphState:
    if decision is None:
        state["interrupt"] = "evidence_review"
        return state
    state["decisions"] = {"evidence": decision.model_dump()}
    state["interrupt"] = None
    return state
