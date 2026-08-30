"""Small, typed LangGraph application workflow primitives."""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .repository.applications import ApplicationMetadata
from .repository.atomic import atomic_write
from .repository.kinds import RecordKind
from .repository.service import list_records, load_record
from .repository.applications import compile_latex

RequirementCategory = Literal["must-have", "preferred", "responsibility", "keyword", "recruiter-concern"]
REQUIREMENTS_PROMPT = "Extract only explicit requirements and preserve short source excerpts."


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
    result = model.invoke(REQUIREMENTS_PROMPT + "\n" + json.dumps(prompt))
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
    unique = {(item.requirement_id, item.source_path, item.excerpt): item for item in candidates}
    state["evidence"] = EvidenceSet(candidates=list(unique.values())).model_dump()
    return state


def rank_evidence(state: GraphState, model: Any) -> GraphState:
    supplied = EvidenceSet.model_validate(state.get("evidence", {}))
    result = model.invoke(supplied.model_dump_json())
    ranked = result if isinstance(result, EvidenceSet) else EvidenceSet.model_validate(result)
    validate_ranked_evidence(ranked, supplied)
    state["evidence"] = ranked.model_dump()
    return state


def validate_ranked_evidence(ranked: EvidenceSet, supplied: EvidenceSet) -> None:
    allowed = {(item.requirement_id, item.source_path, item.excerpt) for item in supplied.candidates}
    if any((item.requirement_id, item.source_path, item.excerpt) not in allowed for item in ranked.candidates):
        raise ValueError("model returned evidence that was not supplied")


def evidence_review(state: GraphState, decision: ReviewDecision | None = None) -> GraphState:
    if decision is None:
        state["interrupt"] = "evidence_review"
        return state
    if decision.action == "approve" and not decision.evidence_ids:
        decision = decision.model_copy(update={"evidence_ids": [str(index) for index, _ in enumerate(EvidenceSet.model_validate(state.get("evidence", {})).candidates)]})
    state["decisions"] = {"evidence": decision.model_dump()}
    state["interrupt"] = None
    return state


def _approved_ids(state: GraphState) -> set[str]:
    return set(state.get("decisions", {}).get("evidence", {}).get("evidence_ids", []))


def draft_cv(state: GraphState, model: Any) -> GraphState:
    result = model.invoke(json.dumps({"job": state["job"], "evidence": state["evidence"], "approved": sorted(_approved_ids(state))}))
    draft = result if isinstance(result, DraftBundle) else DraftBundle.model_validate(result)
    if any(not set(claim.evidence_ids) <= _approved_ids(state) for claim in draft.claims):
        raise ValueError("CV claim uses unapproved evidence")
    state.setdefault("drafts", {})["cv"] = draft.model_dump()
    return state


class NextSteps(BaseModel):
    assessment: str
    evidence_table: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    interview_themes: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    study_plan: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    timing: str


def draft_next_steps(state: GraphState, model: Any) -> GraphState:
    result = model.invoke(json.dumps({"job": state["job"], "requirements": state["requirements"], "evidence": state["evidence"]}))
    steps = result if isinstance(result, NextSteps) else NextSteps.model_validate(result)
    state.setdefault("drafts", {})["next_steps"] = steps.model_dump()
    return state


def render_job_post(state: GraphState) -> str:
    metadata = state["job"]["metadata"]
    lines = ["---", *[f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items() if value not in ("", None)], "---", "", f"<!-- source: {state['job']['source_path']} -->", ""]
    return "\n".join(lines)


def latex_escape(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
    return "".join(replacements.get(char, char) for char in value)


def render_cv(state: GraphState, template: str) -> str:
    draft = DraftBundle.model_validate(state["drafts"]["cv"])
    result = template.replace("TARGET ROLE", latex_escape(state["job"]["metadata"]["role"]))
    result = result.replace("TARGETED SUMMARY", latex_escape(draft.summary))
    claims = "\n".join(f"    \\item {latex_escape(claim.text)}" for claim in draft.claims)
    result = result.replace("RELEVANT, EVIDENCE-BASED ACHIEVEMENT", claims or "")
    return result


def render_cv_source(state: GraphState, template_path: Path) -> str:
    return render_cv(state, template_path.read_text(encoding="utf-8"))


def render_next_steps(state: GraphState) -> str:
    steps = NextSteps.model_validate(state["drafts"]["next_steps"])
    sections = [("Fit assessment", [steps.assessment]), ("Evidence", steps.evidence_table), ("Gaps", steps.gaps), ("Interview themes", steps.interview_themes), ("Questions", steps.questions), ("Study plan", steps.study_plan), ("Risks and timing", steps.risks + [steps.timing])]
    return "\n\n".join(f"## {title}\n\n" + "\n".join(f"- {item}" for item in items) for title, items in sections)


def render_next_steps_file(state: GraphState) -> str:
    return render_next_steps(state) + "\n"


def validate_artifacts(files: dict[str, str], state: GraphState) -> list[str]:
    errors = [name for name in ("job-post.md", "cv.tex", "next-steps.mdx") if name not in files]
    if "cv.tex" in files and "\\documentclass" not in files["cv.tex"]:
        errors.append("cv.tex must contain a document class")
    if "cv.tex" in files and any(token in files["cv.tex"] for token in ("\\write18", "\\input{") ):
        errors.append("unsafe LaTeX command")
    if "job-post.md" in files and "TODO" in files["job-post.md"]:
        errors.append("job post contains TODO")
    if "job-post.md" in files and state.get("job", {}).get("metadata", {}).get("language") and "language:" not in files["job-post.md"]:
        errors.append("job post metadata is incomplete")
    return errors


def final_review(state: GraphState, approved: bool | None = None) -> GraphState:
    if approved is None:
        state["interrupt"] = "final_review"
    elif approved:
        state["approvals"] = {"final": True}
        state["interrupt"] = None
    else:
        state["approvals"] = {"final": False}
        state["interrupt"] = None
    return state


def review_payload(state: GraphState) -> dict[str, Any]:
    return {"diffs": state.get("artifact_paths", []), "validation": state.get("validation", {}), "terra": state.get("drafts", {}).get("terra", []), "compilation": state.get("compilation", {})}


def finalize_application(root: Path, slug: str, files: dict[str, str], state: GraphState) -> Path:
    if state.get("approvals", {}).get("final") is not True:
        raise ValueError("final approval is required")
    errors = validate_artifacts(files, state)
    if errors:
        raise ValueError("cannot finalize invalid artifacts: " + ", ".join(errors))
    target = root / "applications" / slug
    if target.exists():
        raise FileExistsError(f"application already exists: {slug}")
    temporary = root / ".whats-a-cv" / "drafts" / state["thread_id"]
    temporary.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        atomic_write(temporary / name, content)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary.rename(target)
    state["artifact_paths"] = [str(target.relative_to(root) / name) for name in files]
    return target


def terra_review(state: GraphState, model: Any = None) -> list[str]:
    if model is None or not model_settings().review_model:
        return []
    result = model.invoke(json.dumps(state.get("drafts", {})))
    return [str(item) for item in (result if isinstance(result, list) else result.get("findings", []))]


def compile_draft(root: Path, state: GraphState, files: dict[str, str]) -> GraphState:
    applications = root / "applications"
    applications.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="draft-", dir=applications))
    try:
        for name, content in files.items():
            (path / name).write_text(content, encoding="utf-8")
        result = compile_latex(root, path.name) if (path / "cv.tex").exists() else {"status": "error", "error": "cv.tex not found"}
    finally:
        shutil.rmtree(path, ignore_errors=True)
    state["compilation"] = {"status": result.get("status", "error"), "pages": result.get("pages"), "errors": [str(result.get("error", ""))[:500]] if result.get("error") else []}
    return state


def workflow_event(state: GraphState, node: str, status: str = "completed") -> dict[str, Any]:
    event = {"thread_id": state["thread_id"], "node": node, "status": status}
    state.setdefault("events", []).append(event)
    return event


def build_graph(root: Path, *, model: Any = None):
    from langgraph.graph import END, START, StateGraph
    graph = StateGraph(GraphState)
    graph.add_node("ingest_job", lambda state: (workflow_event(state, "ingest_job"), state)[1])
    graph.add_node("extract_requirements", lambda state: (extract_requirements(state, model), workflow_event(state, "extract_requirements"), state)[-1] if model else state)
    graph.add_node("retrieve_evidence", lambda state: (retrieve_evidence(state, root), workflow_event(state, "retrieve_evidence"), state)[-1])
    graph.add_node("evidence_review", lambda state: evidence_review(state))
    graph.add_edge(START, "ingest_job")
    graph.add_edge("ingest_job", "extract_requirements")
    graph.add_edge("extract_requirements", "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "evidence_review")
    graph.add_edge("evidence_review", END)
    return graph.compile()
