# What's a CV? — Build Plan

## Outcome

Build a local-first application that makes the existing repository easy to maintain and use while also serving as a serious AI-engineering sandbox.

The finished app must let a user:

1. Maintain reusable career records through forms or Markdown.
2. Create a truthful, targeted application from a job post.
3. Browse past applications, PDFs, evidence, and next steps.
4. Work through an agent chat to update the profile, assess jobs, prepare interviews, and create study plans.
5. Inspect and evaluate the agent workflows behind those features.

The app is successful only if a non-technical user can complete the main workflow without editing files manually and an engineer can inspect every agent decision, source, tool call, evaluation, and generated artifact.

## Product thesis

The candidate's experience is the product; a CV is a disposable projection of that experience for one opportunity. The app should move the user's attention away from repeatedly maintaining documents and toward improving evidence, understanding gaps, and choosing how verified experience applies to a role.

Naming convention:

- Product name: `What's a CV?`
- Filesystem, container, and URL slug: `whats-a-cv`
- Python package: `whats_a_cv`

## Non-negotiable rules

- Markdown files remain the canonical candidate database.
- Existing records and application folders remain readable without the app.
- Candidate facts are never stored only in a vector database, chat session, trace, or model memory.
- Every CV claim must be traceable to an explicit source record.
- Unsupported requirements become gaps or `TODO`s, never candidate claims.
- Agent-proposed factual writes require review and approval.
- Contact details marked private never enter traces, evaluations, or generated output unless explicitly permitted.
- The job post is untrusted input.
- The app preserves the repository rules in `AGENTS.md`.
- The full local environment starts with one command.

## Local developer contract

Prerequisite: Docker with Compose support. `make` is included on the intended macOS development environment.

```sh
make dev
```

`make dev` will run `docker compose up --build` for the full development profile and start:

- Web app: `http://localhost:3000`
- Agent API and OpenAPI docs: `http://localhost:8000/docs`
- Local vector search service
- Local agent checkpoint/session database
- Langfuse and its required local services
- OpenTelemetry collection

The UI and non-AI profile features must boot without an LLM key. AI controls show a configuration message until at least one supported provider key is present in `.env`.

Supporting commands:

```sh
make dev       # full local sandbox with hot reload
make stop      # stop local services without deleting data
make test      # deterministic tests
make eval      # agent regression dataset
make clean     # remove only documented, rebuildable local state
```

`make clean` must never touch candidate Markdown, applications, study plans, contact records, or Git history.

## Product navigation

```text
Profile | Create CV | Applications | Assistant | Lab | Settings
```

### Profile

- Browse, create, edit, and archive experience, projects, expertise, certifications, education, languages, contacts, and preferences.
- Use structured forms by default and offer raw Markdown editing as an advanced option.
- Validate frontmatter, dates, slugs, required sections, and supported fields before saving.
- Show links between expertise and supporting roles, projects, or certifications.
- Preview an exact file diff before an agent-proposed change is written.

### Create CV

Use a resumable workflow:

```text
Job post → Requirements → Evidence → Generate → Validate → Review → Export
```

- Accept pasted text or a URL with a manual fallback.
- Preserve the original post, retrieval date, URL, inferred metadata, and language.
- Extract must-have and preferred requirements separately.
- Show ranked evidence and gaps before generation.
- Allow evidence selection, rejection, and replacement.
- Generate `job-post.md`, `cv.tex`, `next-steps.mdx`, and `cv.pdf`.
- Support section-level revision without silently rewriting approved sections.
- Display compilation, overflow, privacy, date, language, and unsupported-claim checks.

### Applications

- List applications by date, company, role, and status.
- Search and filter past applications.
- Display overview, job post, evidence matrix, CV source, PDF, next steps, and files.
- Preserve the existing folder contract:

```text
applications/YYYY-MM-DD-company-role/
├── job-post.md
├── cv.tex
├── cv.pdf
└── next-steps.mdx
```

- Read the existing `next-steps.md` variant for backward compatibility, but write `next-steps.mdx` for new applications.
- Store optional application status and private notes in a separate Markdown file so generated deliverables remain stable.

### Assistant

- Provide an ADK-style streaming conversation with session history, tool activity, context chips, and artifact previews.
- Answer questions using selected profile records, applications, or the whole repository.
- Propose new or updated profile records from conversation.
- Start the CV-generation LangGraph when asked to prepare an application.
- Create interview preparation and study plans as Markdown artifacts.
- Require approval before modifying canonical files.
- Make tool errors and incomplete evidence visible instead of hiding them behind a generic response.

### Lab

- Inspect LangGraph state and transitions.
- Inspect ADK agents, tools, sessions, events, and artifacts.
- Browse Langfuse traces, token use, latency, prompt versions, and scores.
- Run saved evaluation cases and compare models or prompts.
- Rebuild and inspect the evidence index.
- Replay a workflow from a checkpoint without rewriting approved files.

## System architecture

```text
┌───────────────────────────┐
│ Next.js + TypeScript UI   │
└─────────────┬─────────────┘
              │ HTTP + SSE
┌─────────────▼─────────────┐
│ FastAPI agent service     │
│                           │
│  ADK conversational agent │
│          │                │
│          └── LangGraph CV │
│                           │
│  LangChain integrations   │
│  Pydantic validation      │
└──────┬──────────┬─────────┘
       │          │
┌──────▼──────┐ ┌─▼────────────────┐
│ Markdown FS │ │ Derived services │
│ + artifacts │ │ SQLite / vector  │
└─────────────┘ │ Langfuse / OTel  │
                └──────────────────┘
```

### Responsibility by tool

| Tool | Responsibility |
| --- | --- |
| Next.js | Product UI, previews, diffs, and streaming progress |
| FastAPI | Typed API, streaming endpoints, health checks, and repository boundary |
| Pydantic | Request, record, graph-state, and structured-output validation |
| LangGraph | Durable CV creation, checkpoints, branching, retries, and human review |
| Google ADK | Conversational assistant, sessions, routing, tools, and artifacts |
| LangChain | Model integrations, structured outputs, documents, retrievers, and shared tool conventions |
| SQLite | Local chat sessions and LangGraph checkpoints, never canonical facts |
| Qdrant | Rebuildable semantic evidence index |
| Langfuse | Traces, prompt versions, experiments, costs, and evaluations |
| OpenTelemetry | Framework-neutral trace propagation across web, API, agents, and tools |
| `latexmk` | Repeatable PDF compilation from the existing moderncv template |
| MCP | Reuse the safe repository tools from Codex and other agent clients |
| Docker Compose | Reproducible one-command local environment |

### Deliberate overlap

ADK and LangGraph are both orchestration technologies, but they do not duplicate responsibilities here:

- ADK owns open-ended conversation and agent routing.
- LangGraph owns the controlled, resumable application workflow.
- ADK invokes the compiled LangGraph workflow as a tool.
- LangChain supplies shared integrations rather than owning orchestration.

If that boundary cannot be maintained in implementation, remove the duplicate path instead of keeping two competing workflows.

## Storage model

### Canonical, portable files

```text
contact/
experience/
education/
certifications/
projects/
expertise/
languages/
preferences.md
applications/
study-plans/
interview-plans/
```

### Derived local state

```text
.whats-a-cv/
├── state.db           # sessions, checkpoints, and application UI state
├── index/             # rebuild metadata and local index state
├── cache/             # fetched pages and temporary generation output
└── logs/              # local development logs
```

Derived state must be ignored by Git and safely rebuildable. A missing `.whats-a-cv/` directory must not lose candidate facts or completed applications.

### Safe repository service

All app, agent, graph, and MCP file access goes through one Python repository module. It must:

- Resolve paths beneath approved repository directories.
- Reject traversal, symlink escape, hidden-path, and unsupported-extension writes.
- Parse and validate frontmatter.
- Write atomically through a temporary sibling file and rename.
- Produce a diff before mutation.
- Keep contact records out of logs and traces.
- Never overwrite an application folder without explicit approval.

## Agent design

### ADK agents

Start with one root agent and three focused delegates:

| Agent | Scope |
| --- | --- |
| What's a CV? | Route requests, maintain conversation context, and present approvals |
| Profile Curator | Read profile evidence and propose record changes |
| Application Coach | Assess roles, inspect prior applications, and invoke the CV graph |
| Learning Coach | Create focused study and interview plans from confirmed gaps |

Agents do not receive direct filesystem access. They receive typed tools from the repository service.

### Shared tools

- `list_records`
- `read_record`
- `search_evidence`
- `propose_record_change`
- `approve_record_change`
- `read_application`
- `analyze_job_post`
- `start_application_workflow`
- `resume_application_workflow`
- `compile_cv`
- `save_study_plan`
- `save_interview_plan`

Read tools can execute immediately. Canonical writes and application finalization always interrupt for approval.

### LangGraph application state

The graph state should contain structured data, not formatted prompt text:

- Job-post metadata and original content reference
- Extracted must-have and preferred requirements
- Evidence candidates with source paths and excerpts
- User evidence decisions
- Draft sections
- Validation results
- Compile results
- Approval state
- Final artifact paths

Workflow nodes:

1. `ingest_job`
2. `extract_requirements`
3. `retrieve_evidence`
4. `rank_evidence`
5. `review_evidence`
6. `draft_application`
7. `validate_application`
8. `compile_cv`
9. `review_artifacts`
10. `write_application`

Use LangGraph interrupts at `review_evidence` and `review_artifacts`. Retriable network or model failures retry with limits; validation failures return to the relevant drafting node; unexpected failures stop with visible state.

### Skills

Create repository-local skills only after their workflow exists in code:

- `manage-profile`
- `prepare-application`
- `career-coach`
- `evaluate-whats-a-cv`

Each skill documents when to use the workflow, accepted inputs, tools, approval boundaries, outputs, and failure behavior. `AGENTS.md` remains authoritative when a skill and repository rule overlap.

## Retrieval plan

1. Begin with exact metadata filters and lexical search over Markdown.
2. Add embeddings and Qdrant as a derived evidence index.
3. Combine lexical and semantic candidates before ranking.
4. Always return source file, section, and supporting excerpt.
5. Never treat similarity as proof that a candidate has a skill.
6. Provide an index rebuild command and stale-index indicator.

The small corpus makes lexical retrieval a valid baseline. Semantic retrieval earns its place through measured evaluation improvement, not by replacing traceability.

## Design system

Create a compact editorial interface with shared CSS tokens rather than adopting a large component system immediately.

### Foundations

- Neutral surfaces with a restrained blue accent.
- Clear Strong, Partial, Gap, and Unverified states.
- Accessible contrast, keyboard navigation, visible focus, and labelled controls.
- Comfortable long-form reading with dense evidence tables.
- Responsive review views; authoring remains desktop-first.

### Core components

- App shell and navigation
- Record list and record editor
- Markdown preview
- Requirement/evidence matrix
- Evidence source chip
- Status badge
- Diff viewer
- Agent message and tool-event cards
- Approval card
- Workflow stepper
- CV/PDF preview
- Validation panel
- Empty, loading, and error states

## API surface

Initial endpoints:

```text
GET    /health
GET    /records/{kind}
GET    /records/{kind}/{slug}
POST   /records/{kind}/proposals
POST   /proposals/{id}/approve
POST   /proposals/{id}/reject
GET    /applications
GET    /applications/{slug}
POST   /workflows/applications
GET    /workflows/{thread_id}
POST   /workflows/{thread_id}/resume
POST   /applications/{slug}/compile
POST   /chat/sessions
GET    /chat/sessions/{id}
POST   /chat/sessions/{id}/messages
GET    /events/{run_id}                 # SSE
POST   /indexes/evidence/rebuild
GET    /lab/traces/{trace_id}
POST   /evals/run
```

Generate the TypeScript client from FastAPI's OpenAPI document rather than maintaining request types twice.

## Build phases

Each phase ends with a usable vertical slice and a runnable check. Later phases must not be required to use earlier non-AI features.

### Phase 0 — Decisions and runnable skeleton

Deliver:

- `web/` Next.js application.
- `agent/` Python package managed by `uv`.
- Dockerfiles, Compose configuration, `.env.example`, and Makefile.
- Web and API health checks.
- Hot reload through `make dev`.
- ADRs for Markdown canonical storage, orchestration boundaries, and approval-based writes.

Acceptance:

- A clean clone starts with `make dev` after Docker is available.
- The home screen and `/health` work without an LLM key.
- Containers stop cleanly without touching repository content.

### Phase 1 — Repository service

Deliver:

- Typed schemas for every existing record template.
- Parser and serializer for Markdown plus YAML frontmatter.
- Read, list, validate, diff, and atomic-write operations.
- Compatibility reads for `next-steps.md` and canonical writes to `next-steps.mdx`.
- Safe-path and privacy enforcement.
- MCP server exposing read tools and approval-based proposal tools.

Acceptance:

- Every current source record parses or reports an actionable validation error.
- A serialize/parse round trip preserves supported content.
- Traversal and symlink escape tests fail safely.
- Contact values never appear in test traces or logs.

### Phase 2 — Profile workspace and design system

Deliver:

- Product shell and reusable visual tokens.
- Profile navigation and searchable record lists.
- Forms for all profile record types.
- Raw Markdown preview/editor.
- Create, edit, validate, diff, approve, and save flow.
- Evidence links between expertise and source records.

Acceptance:

- The user can add an experience and certification without opening an editor.
- Invalid dates and incomplete required fields cannot be saved silently.
- A saved record remains a clean, reusable Markdown file.
- Keyboard-only use covers the complete edit flow.

### Phase 3 — Applications workspace

Deliver:

- Job-post ingestion UI and URL fallback behavior.
- Past-application list and detail tabs.
- CV source, PDF, next-steps, evidence, and file views.
- `latexmk` compilation service with captured errors and page count.
- Application status and notes stored separately from generated artifacts.

Acceptance:

- The existing Option application is readable in the UI.
- The existing `next-steps.md` is displayed without migration.
- A known CV compiles and the resulting PDF is previewable.
- Compilation failures produce actionable output.

### Phase 4 — LangGraph CV workflow

Deliver:

- Typed graph state and the ten workflow nodes.
- SQLite checkpointer and stable thread IDs.
- Streaming workflow events.
- Human interrupts for evidence and final review.
- Application generation from `TEMPLATE.tex`.
- Deterministic quality gates before final write.

Acceptance:

- A workflow can pause, survive a service restart, and resume.
- Rejected evidence does not return unless the user resets the decision.
- Unsupported claims fail validation.
- Finalization produces the required application folder and artifacts.

### Phase 5 — ADK assistant

Deliver:

- Root agent and three delegates.
- Persistent local sessions and streamed events.
- Shared repository tools.
- Proposed-change approval cards.
- LangGraph application workflow exposed as an ADK tool.
- Saved study and interview plans.

Acceptance:

- “Add this certification” results in a reviewable Markdown proposal.
- Rejecting a proposal makes no canonical file change.
- “Prepare an application” enters the same LangGraph flow used by Create CV.
- “Make a study plan for Terraform” saves a useful Markdown artifact only when requested.

### Phase 6 — Retrieval and evidence ranking

Deliver:

- Lexical retrieval baseline.
- Markdown chunking with source metadata.
- Qdrant embedding index and rebuild command.
- Hybrid candidate retrieval and evidence ranking.
- Index freshness indicator.

Acceptance:

- Every result includes a resolvable source file and excerpt.
- Deleting the vector index and rebuilding it produces a working app.
- Retrieval evaluation compares lexical and hybrid results.
- Semantic retrieval ships only if it improves the agreed evidence metrics.

### Phase 7 — Observability and prompt management

Deliver:

- OpenTelemetry trace propagation from browser request through tools.
- Langfuse traces grouped by user session and workflow run.
- Stable names for agent, graph node, model, retrieval, compile, and approval spans.
- Token, latency, model, prompt version, and cost metadata.
- Redaction before telemetry export.

Acceptance:

- One trace explains a complete application run.
- No private contact value appears in Langfuse.
- A failed node is identifiable without reproducing the run locally.
- Two prompt versions can be compared against the same dataset.

### Phase 8 — Evaluations

Deliver:

- Versioned evaluation cases derived from sanitized or synthetic job posts.
- Deterministic validators and agent-quality graders.
- ADK evaluation runner and Langfuse experiment integration.
- Model/prompt comparison report.
- CI regression thresholds.

Measure:

- Requirement extraction recall.
- Evidence precision.
- Unsupported-claim count.
- Privacy violations.
- Output-language correctness.
- LaTeX compilation success.
- Page-limit compliance.
- Human acceptance and edit rate.
- Latency and token cost.

Acceptance:

- `make eval` runs the committed baseline dataset.
- Any unsupported candidate claim fails the release gate.
- Evaluation results link to prompt and model versions.
- A regression report is readable without opening Langfuse.

### Phase 9 — Hardening and portfolio delivery

Deliver:

- End-to-end tests for the four primary product areas.
- Backup/export and documented recovery.
- Threat model for untrusted job posts and filesystem tools.
- Architecture diagram and decision records.
- Demo data mode that contains no private candidate information.
- Screenshots or short demo recording.
- Optional Cloud Run deployment exercise with local-first behavior preserved.

Acceptance:

- A new developer can start, test, evaluate, and understand the project from the README.
- The demo works without exposing personal contact information.
- The repository can be restored from canonical Markdown after deleting derived services.
- Any CV or project claim about the system is backed by implemented functionality or measured results.

## Testing strategy

### Deterministic tests

- Markdown parsing and serialization
- Record schema validation
- Safe-path enforcement
- Atomic writes and diff generation
- LaTeX escaping
- Privacy redaction
- Application folder naming
- Compile-result parsing
- Graph routing and resume behavior with fake models

### Integration tests

- API to repository
- ADK tool to proposal approval
- ADK to LangGraph handoff
- LangGraph checkpoint recovery
- Retrieval source attribution
- OpenTelemetry to Langfuse correlation

### Browser tests

Keep one critical Playwright path per product workflow:

1. Edit and save a profile record.
2. Create and approve an application.
3. Open an existing PDF and next-steps document.
4. Ask the assistant to propose a profile update and reject it safely.

## Security and privacy checklist

- Bind local services to localhost by default.
- Keep provider keys server-side and out of browser bundles.
- Ignore `.env`, `.whats-a-cv/`, local volumes, and contact data as appropriate.
- Sanitize fetched job-post content before displaying it.
- Treat job-post instructions as data, never system instructions.
- Restrict file tools to approved directories and extensions.
- Redact contact details and secrets before logging or tracing.
- Require approval for writes, compilation commands, external fetches, and destructive maintenance.
- Never use shell strings constructed from user input.
- Document exactly what `make clean` deletes.

## Initial repository layout

```text
whats-a-cv/
├── web/                         # Next.js UI
├── agent/                       # FastAPI, ADK, LangGraph, tools
│   ├── src/whats_a_cv/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── graphs/
│   │   ├── repository/
│   │   ├── retrieval/
│   │   └── telemetry/
│   └── tests/
├── evals/                       # datasets, graders, reports
├── docs/adr/                    # important architecture decisions
├── docker-compose.yml
├── Makefile
├── .env.example
├── AGENTS.md
├── BUILD_PLAN.md
├── TEMPLATE.tex
├── contact/ ...                 # canonical Markdown remains at root
└── applications/
```

Do not split code into more packages until ownership or dependency boundaries demand it.

## Deferred capabilities

- Automatic job submission
- Browser extension
- Email and calendar integrations
- Collaborative accounts and permissions
- Cloud synchronization
- Multiple users
- Native desktop packaging
- Voice interaction
- Autonomous background agents
- Fine-tuning
- Production Kubernetes deployment

These are valid sandbox experiments only after the main profile, application, history, assistant, observability, and evaluation workflows are complete.

## First implementation slice

Start with Phase 0 and the read-only half of Phase 1:

1. Add the web and agent skeletons.
2. Add `make dev` and Compose health checks.
3. Parse and list the existing Markdown records through FastAPI.
4. Render those records in a read-only Profile screen.
5. Leave agent frameworks installed only when the first workflow that uses each one is implemented.

This slice proves the storage boundary, two-service development loop, and one-command startup before agent complexity is introduced.
