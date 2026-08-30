# What's a CV? — Atomic Task List

This file turns `BUILD_PLAN.md` into resumable work packets sized for GPT-5.6 Luna. Complete tasks in dependency order. One checked task should represent one tested outcome and, ideally, one commit.

## How to resume

Give the coding agent this prompt, replacing the task ID:

```text
Complete only task P0-01 from TASKS.md.

Read AGENTS.md, BUILD_PLAN.md, the selected task, and only the files needed for it.
Respect existing user changes. Do not start another task.
Run the task's check. Mark its checkbox only if the check passes.
If blocked, leave it unchecked and append a short BLOCKED note with the exact cause.
End with changed files, check result, and the next unblocked task ID.
```

Recommended model settings:

- Default implementation: `gpt-5.6-luna`, reasoning `medium`, low verbosity.
- Small mechanical tasks: Luna, reasoning `low`.
- Tasks marked **Terra review**: `gpt-5.6-terra`, reasoning `medium`.
- Do not use multi-agent execution for one task.

## Completion protocol

1. Read `AGENTS.md` and the relevant section of `BUILD_PLAN.md`.
2. Inspect `git status --short`; preserve unrelated changes.
3. Confirm every dependency is checked.
4. Implement only the selected task.
5. Run its check and the smallest relevant regression check.
6. Mark the task `[x]` only after both pass.
7. If context is running low, do not begin another task.
8. Never mark work complete based only on code inspection when a runnable check exists.

Status conventions:

- `[ ]` ready or pending.
- `[x]` implemented and checked.
- `BLOCKED:` appended to an unchecked task explains an external blocker.

## Phase 0 — Runnable skeleton

- [x] **P0-01 — Ignore derived local state.** Add `.whats-a-cv/`, `.env`, framework build output, and local Compose volumes to `.gitignore` without weakening existing contact privacy rules. Dependencies: none. Check: `git check-ignore .whats-a-cv/state.db .env web/.next/`.
- [x] **P0-02 — Add environment template.** Create `.env.example` with empty `OPENAI_API_KEY`, Luna/Terra model IDs, local URLs, and no secrets. Dependencies: P0-01. Check: verify `.env.example` is tracked and `.env` is ignored.
- [x] **P0-03 — Record canonical-storage decision.** Add `docs/adr/0001-markdown-is-canonical.md` covering canonical and derived data boundaries. Dependencies: none. Check: document names every canonical root from `BUILD_PLAN.md`.
- [x] **P0-04 — Record orchestration decision.** Add ADR defining ADK for conversation, LangGraph for the application workflow, and LangChain for integrations. Dependencies: none. Check: document contains one owner for each responsibility and no duplicate CV workflow.
- [x] **P0-05 — Record approval decision.** Add ADR defining read actions, proposal actions, approval-required writes, and destructive-action boundaries. Dependencies: none. Check: document explicitly forbids direct agent filesystem access.
- [x] **P0-06 — Scaffold Python package.** Create `agent/pyproject.toml`, `agent/src/whats_a_cv/__init__.py`, and a locked Python version using `uv`; include FastAPI, Uvicorn, Pydantic, and pytest only. Dependencies: P0-02. Check: `cd agent && uv run python -c "import whats_a_cv"`.
- [x] **P0-07 — Add FastAPI health endpoint.** Create the smallest app exposing `GET /health` with a typed `{status: "ok"}` response. Dependencies: P0-06. Check: `cd agent && uv run python -m pytest tests/test_health.py`.
- [x] **P0-08 — Containerize the agent service.** Add `agent/Dockerfile` with a non-root runtime and Uvicorn startup. Dependencies: P0-07. Check: `docker build -t whats-a-cv-agent ./agent`.
- [x] **P0-09 — Scaffold Next.js web app.** Create `web/` with TypeScript, App Router, npm lockfile, lint, and no component framework. Dependencies: P0-02. Check: `cd web && npm run build`.
- [x] **P0-10 — Add web health route.** Add `GET /api/health` returning `{status: "ok"}`. Dependencies: P0-09. Check: add and run the smallest route test or build-time smoke check.
- [x] **P0-11 — Containerize the web app.** Add `web/Dockerfile` with development and production stages. Dependencies: P0-09. Check: `docker build -t whats-a-cv-web ./web`.
- [x] **P0-12 — Compose the core services.** Add `docker-compose.yml` for web and agent with repository mounts, health checks, localhost ports, and persistent derived state only. Dependencies: P0-08, P0-11. Check: `docker compose config`.
- [x] **P0-13 — Add the one-line launcher.** Add `make dev` to run the Compose development stack with build and hot reload. Dependencies: P0-12. Check: `make dev`, then both health endpoints return 200.
- [x] **P0-14 — Add lifecycle commands.** Add safe `make stop`, `make test`, and `make clean`; clean may remove only documented derived state. Dependencies: P0-13. Check: inspect `make -n clean` and confirm no canonical directory can be targeted.
- [x] **P0-15 — Document local startup.** Update `README.md` with prerequisites, `make dev`, URLs, optional API-key setup, and stop command. Dependencies: P0-13. Check: follow the documented startup from a stopped stack.
- [x] **P0-16 — Skeleton review.** **Terra review.** Audit Phase 0 against the three ADRs and one-command requirement; fix only confirmed Phase 0 defects. Dependencies: P0-01 through P0-15. Check: `make test` and `docker compose config`.

## Phase 1 — Safe Markdown repository service

- [x] **P1-01 — Define record kinds.** Add a closed enum mapping contact, experience, education, certifications, projects, expertise, and languages to approved roots. Dependencies: P0-16. Check: unit test rejects an unknown kind.
- [x] **P1-02 — Define source locations.** Add a typed source-location model containing relative path and optional section heading. Dependencies: P1-01. Check: Pydantic round-trip test.
- [x] **P1-03 — Split frontmatter safely.** Implement a parser that separates YAML frontmatter and Markdown body without interpreting body content. Dependencies: P1-01. Check: tests for valid, missing, and unclosed frontmatter.
- [x] **P1-04 — Parse frontmatter.** Add YAML parsing with mapping-only output and actionable errors. Dependencies: P1-03. Check: malformed YAML test contains file context.
- [x] **P1-05 — Serialize records.** Serialize frontmatter plus body with stable field ordering and a final newline. Dependencies: P1-04. Check: snapshot one template round trip.
- [x] **P1-06 — Preserve record content.** Add corpus round-trip tests proving parse/serialize/parse semantic equality for every tracked source record. Dependencies: P1-05. Check: `cd agent && uv run pytest tests/repository/test_round_trip.py`.
- [x] **P1-07 — Validate filenames.** Add lowercase hyphenated slug validation and reserved `_template.md` handling. Dependencies: P1-01. Check: tests for valid, uppercase, traversal-like, and template filenames.
- [x] **P1-08 — Validate ISO dates.** Support `YYYY-MM`, `YYYY-MM-DD`, and `present` only where allowed. Dependencies: P1-01. Check: boundary and invalid-date tests.
- [x] **P1-09 — Enforce approved paths.** Resolve record paths beneath their approved roots and reject absolute paths, `..`, hidden paths, and unsupported extensions. Dependencies: P1-01, P1-07. Check: traversal tests.
- [x] **P1-10 — Reject symlink escapes.** Prevent reads and writes through symlinks escaping the repository. Dependencies: P1-09. Check: temporary symlink escape test.
- [x] **P1-11 — Add atomic writes.** Write through a temporary sibling file, fsync where supported, and replace atomically. Dependencies: P1-09. Check: failed-write test leaves the original unchanged.
- [x] **P1-12 — Generate unified diffs.** Return a stable relative-path diff for proposed content without writing it. Dependencies: P1-05. Check: exact diff assertion for one changed field.
- [x] **P1-13 — Model experience records.** Add the schema required by `experience/_template.md`. Dependencies: P1-04, P1-08. Check: parse every experience record.
- [x] **P1-14 — Model education records.** Add the schema required by `education/_template.md`. Dependencies: P1-04, P1-08. Check: parse every education record.
- [x] **P1-15 — Model certification records.** Add the schema required by `certifications/_template.md`. Dependencies: P1-04, P1-08. Check: parse every certification record.
- [x] **P1-16 — Model project records.** Add the schema required by `projects/_template.md`. Dependencies: P1-04, P1-08. Check: parse the template and all project records.
- [x] **P1-17 — Model expertise records.** Add the schema required by `expertise/_template.md` and preserve evidence bullets. Dependencies: P1-02, P1-04. Check: parse every expertise record.
- [x] **P1-18 — Model language records.** Add the schema required by `languages/_template.md`. Dependencies: P1-04. Check: parse every language record.
- [x] **P1-19 — Model contact records.** Add the contact schema and an inclusion flag without logging values. Dependencies: P1-04. Check: caplog test contains no contact value.
- [x] **P1-20 — Model preferences.** Parse and serialize `preferences.md` separately from CV-eligible records. Dependencies: P1-03, P1-05. Check: round-trip `preferences.md` without exposing it as CV evidence.
- [x] **P1-21 — List records.** Implement repository listing by kind with slug, title, validation state, and relative path. Dependencies: P1-13 through P1-20. Check: expected tracked record counts.
- [x] **P1-22 — Read one record.** Implement typed record retrieval by kind and slug. Dependencies: P1-21. Check: known record succeeds and unknown slug returns a typed not-found error.
- [x] **P1-23 — Validate the whole profile.** Return all source errors in one report instead of stopping at the first file. Dependencies: P1-21. Check: injected two-error fixture returns both errors.
- [x] **P1-24 — Create proposal storage.** Add a SQLite proposal table containing target path, old hash, proposed content, diff, status, and timestamps. Dependencies: P1-12. Check: migration and repository test.
- [x] **P1-25 — Create change proposals.** Add a service that validates content and stores a proposal without changing the target. Dependencies: P1-23, P1-24. Check: target hash is unchanged after proposal creation.
- [x] **P1-26 — Approve change proposals.** Approve only a pending proposal whose old hash still matches, then use atomic write. Dependencies: P1-11, P1-25. Check: stale-hash approval fails without writing.
- [x] **P1-27 — Reject change proposals.** Record rejection and make later approval impossible. Dependencies: P1-25. Check: rejected proposal leaves the target unchanged.
- [x] **P1-28 — Expose record reads.** Add `GET /records/{kind}` and `GET /records/{kind}/{slug}`. Dependencies: P1-21, P1-22. Check: API tests for success, validation error, and not found.
- [x] **P1-29 — Expose proposal actions.** Add create, inspect, approve, and reject proposal endpoints. Dependencies: P1-25 through P1-27. Check: API lifecycle test.
- [x] **P1-30 — Expose MCP read tools.** Add `list_records` and `read_record` through one local MCP server. Dependencies: P1-28. Check: MCP tool contract test with no network dependency.
- [x] **P1-31 — Expose MCP proposal tools.** Add proposal creation and status tools, but no direct write tool. Dependencies: P1-29, P1-30. Check: MCP manifest contains no unrestricted filesystem tool.
- [x] **P1-32 — Repository security review.** **Terra review.** Audit path handling, atomic writes, contact redaction, and proposal races; fix only demonstrated issues and add regression tests. Dependencies: P1-01 through P1-31. Check: full agent test suite.

## Phase 2 — Profile workspace and design system

- [x] **P2-01 — Add design tokens.** Define light-theme CSS variables for typography, spacing, color, radius, focus, and Strong/Partial/Gap/Unverified states. Dependencies: P0-09. Check: production web build.
- [x] **P2-02 — Build the app shell.** Add sidebar, header, main landmark, responsive content region, and skip link. Dependencies: P2-01. Check: keyboard focus reaches skip link and navigation.
- [x] **P2-03 — Add primary routes.** Create empty routes for Profile, Create CV, Applications, Assistant, Lab, and Settings. Dependencies: P2-02. Check: every sidebar link returns 200.
- [x] **P2-04 — Generate the API client.** Generate TypeScript request types from FastAPI OpenAPI and add a repeatable npm command. Dependencies: P1-29, P2-03. Check: generated client has no manual edits and web type-check passes.
- [x] **P2-05 — Add record-kind navigation.** Add Profile tabs/counts for every record kind. Dependencies: P1-28, P2-04. Check: counts match API fixtures.
- [x] **P2-06 — Build the record list.** Show title, subtitle, validation state, and updated path with loading, empty, and error states. Dependencies: P2-05. Check: component test covers all four states.
- [ ] **P2-07 — Build the record detail route.** Load one typed record by kind and slug and show its source path. Dependencies: P2-06. Check: valid and missing record tests.
- [ ] **P2-08 — Add experience editor.** Implement fields and repeatable achievements/skills matching the existing template. Dependencies: P2-07, P1-13. Check: edit fixture serializes to valid experience Markdown.
- [ ] **P2-09 — Add education editor.** Implement fields matching the education template. Dependencies: P2-07, P1-14. Check: edit fixture passes API validation.
- [ ] **P2-10 — Add certification editor.** Implement fields matching the certification template. Dependencies: P2-07, P1-15. Check: edit fixture passes API validation.
- [ ] **P2-11 — Add project editor.** Implement context, contributions, outcomes, and skills fields. Dependencies: P2-07, P1-16. Check: edit fixture passes API validation.
- [ ] **P2-12 — Add expertise editor.** Implement name, category, last-used, and evidence bullets. Dependencies: P2-07, P1-17. Check: edit fixture preserves evidence bullets.
- [ ] **P2-13 — Add language editor.** Implement language and proficiency fields. Dependencies: P2-07, P1-18. Check: edit fixture passes API validation.
- [ ] **P2-14 — Add private contact editor.** Mask values by default and show inclusion status explicitly. Dependencies: P2-07, P1-19. Check: browser test confirms value is not present before reveal.
- [ ] **P2-15 — Add preferences editor.** Keep preferences visually separate from CV evidence. Dependencies: P2-07, P1-20. Check: UI labels state preferences are not copied automatically.
- [ ] **P2-16 — Add raw Markdown preview.** Show generated Markdown from form state without writing. Dependencies: P2-08 through P2-15. Check: toggling preview preserves unsaved form state.
- [ ] **P2-17 — Add proposal diff review.** Submit form changes as proposals and show the server-produced unified diff. Dependencies: P1-29, P2-16. Check: opening review does not modify the source file.
- [ ] **P2-18 — Add approve/reject controls.** Apply or reject a proposal and refresh the record state. Dependencies: P2-17. Check: browser test covers approval and rejection.
- [ ] **P2-19 — Add create-record flow.** Derive a suggested slug, require user confirmation, and create through the proposal API. Dependencies: P2-18. Check: create one fixture record in a temporary repository.
- [ ] **P2-20 — Show validation summaries.** Display actionable per-field and corpus-level validation errors. Dependencies: P1-23, P2-06. Check: two server errors render without losing either message.
- [ ] **P2-21 — Add evidence links.** Make expertise evidence references navigate to their source records where resolvable. Dependencies: P2-12. Check: known source link opens the correct record.
- [ ] **P2-22 — Profile accessibility check.** Test keyboard use, labels, focus, contrast, and error announcements for one complete edit flow. Dependencies: P2-01 through P2-21. Check: Playwright accessibility smoke test.

## Phase 3 — Applications and PDF workspace

- [ ] **P3-01 — Define application metadata.** Add typed company, role, location, date, language, URL, retrieval date, status, and artifact paths. Dependencies: P1-02. Check: parse the existing application folder.
- [ ] **P3-02 — Read application bundles.** List expected and extra files without interpreting untrusted content as instructions. Dependencies: P3-01, P1-09. Check: existing Option bundle is returned.
- [ ] **P3-03 — Support legacy next steps.** Read `next-steps.md` when `.mdx` is absent and prefer `.mdx` when both exist. Dependencies: P3-02. Check: two fixtures cover fallback and preference.
- [ ] **P3-04 — Expose application reads.** Add list and detail API endpoints. Dependencies: P3-02, P3-03. Check: API tests cover existing, missing, and malformed bundles.
- [ ] **P3-05 — Build applications list.** Show date, company, role, status, PDF presence, and outstanding TODO indicator. Dependencies: P3-04, P2-04. Check: existing Option application appears.
- [ ] **P3-06 — Build application overview.** Show metadata, artifact health, and requirement summary placeholder. Dependencies: P3-05. Check: missing optional files produce warnings, not crashes.
- [ ] **P3-07 — Add job-post tab.** Render saved Markdown as inert content and link the source URL safely. Dependencies: P3-06. Check: embedded HTML/script fixture cannot execute.
- [ ] **P3-08 — Add CV source tab.** Show editable-looking but read-only LaTeX with download. Dependencies: P3-06. Check: source downloads byte-for-byte.
- [ ] **P3-09 — Add PDF tab.** Preview an existing PDF and offer download with a non-preview fallback. Dependencies: P3-06. Check: existing PDF returns the correct content type.
- [ ] **P3-10 — Add next-steps tab.** Render `.mdx` or legacy `.md` as safe Markdown without executing components. Dependencies: P3-03, P3-06. Check: legacy file renders.
- [ ] **P3-11 — Add files tab.** Show approved bundle files, sizes, and paths without browsing outside the bundle. Dependencies: P3-02, P3-06. Check: traversal-shaped filename fixture is rejected.
- [ ] **P3-12 — Store application status.** Add an optional separate Markdown metadata file and proposal-based status updates. Dependencies: P1-25, P3-01. Check: updating status does not change generated artifacts.
- [ ] **P3-13 — Add private application notes.** Store notes separately, keep them out of model context by default, and edit through proposals. Dependencies: P3-12. Check: read_application tool omits notes unless explicitly requested.
- [ ] **P3-14 — Ingest pasted job text.** Add API and UI draft state for original text plus editable metadata; do not create an application yet. Dependencies: P2-03, P3-01. Check: pasted text survives page navigation in draft state.
- [ ] **P3-15 — Fetch job URLs safely.** Add server-side HTTP fetching with scheme allowlist, private-network blocking, size/time limits, and manual-paste fallback. Dependencies: P3-14. Check: tests block localhost/private IPs and accept a mocked public page.
- [ ] **P3-16 — Normalize fetched content.** Extract readable text, preserve the original URL/retrieval date, and strip active content. Dependencies: P3-15. Check: hostile HTML fixture becomes inert text.
- [ ] **P3-17 — Compile LaTeX safely.** Invoke `latexmk` with fixed arguments, explicit working directory, timeout, and captured output; never construct a shell string. Dependencies: P3-02. Check: compile a fixture and reject an out-of-root path.
- [ ] **P3-18 — Expose compilation.** Add compile/status API endpoints returning PDF path, page count, warnings, and sanitized errors. Dependencies: P3-17. Check: success and deliberate-failure API tests.
- [ ] **P3-19 — Add compile UI.** Trigger compilation, stream/poll state, preview success, and show actionable errors. Dependencies: P3-09, P3-18. Check: browser test covers one success and one error.
- [ ] **P3-20 — Applications workspace review.** **Terra review.** Audit untrusted-content rendering, URL fetching, path boundaries, and compilation. Dependencies: P3-01 through P3-19. Check: full web and agent tests.

## Phase 4 — Luna-backed LangGraph application workflow

- [ ] **P4-01 — Add model dependencies.** Add LangGraph, LangChain OpenAI integration, and the OpenAI SDK to the Python package; record resolved versions. Dependencies: P3-20. Check: imports succeed under `uv run`.
- [ ] **P4-02 — Add model configuration.** Default to `gpt-5.6-luna`, allow an optional Terra review model, validate reasoning effort, and fail AI actions clearly when no key exists. Dependencies: P4-01, P0-02. Check: configuration tests with and without key.
- [ ] **P4-03 — Wrap the Responses API.** Add one LangChain/OpenAI model factory with structured-output and streaming support; no provider abstraction beyond configured models. Dependencies: P4-02. Check: fake-client contract test.
- [ ] **P4-04 — Define requirement output.** Add structured models for must-have, preferred, responsibility, keyword, and recruiter concern with source excerpts. Dependencies: P4-03. Check: invalid category/output fails validation.
- [ ] **P4-05 — Define evidence output.** Add evidence candidates with requirement ID, source path, section, excerpt, relevance reason, and confidence. Dependencies: P4-04, P1-02. Check: missing source reference fails validation.
- [ ] **P4-06 — Define graph state.** Add JSON-serializable state for job, requirements, evidence, decisions, drafts, validation, compilation, approvals, and artifact paths. Dependencies: P4-04, P4-05. Check: state round-trip test.
- [ ] **P4-07 — Add SQLite checkpointing.** Persist graph checkpoints under `.whats-a-cv/state.db` with stable thread IDs. Dependencies: P4-06. Check: checkpoint survives process recreation.
- [ ] **P4-08 — Implement `ingest_job`.** Validate pasted/fetched draft metadata and store original content by reference. Dependencies: P3-14 through P3-16, P4-06. Check: node test with valid and incomplete drafts.
- [ ] **P4-09 — Implement `extract_requirements`.** Use Luna structured output and preserve source excerpts. Dependencies: P4-04, P4-08. Check: fake response maps to typed requirements.
- [ ] **P4-10 — Implement `retrieve_evidence` baseline.** Search canonical records lexically and return source-backed candidates without an LLM. Dependencies: P1-21, P4-05, P4-09. Check: known Python requirement finds explicit Python evidence.
- [ ] **P4-11 — Implement `rank_evidence`.** Ask Luna to rank only supplied candidates; forbid new evidence and validate every returned source. Dependencies: P4-10. Check: invented source is rejected.
- [ ] **P4-12 — Implement evidence review interrupt.** Pause with requirements, ranked evidence, and gaps; accept approve, replace, reject, and notes. Dependencies: P4-07, P4-11. Check: interrupt/resume unit test.
- [ ] **P4-13 — Implement CV drafting.** Generate structured summary, experience selections, bullets, and skills using only approved evidence. Dependencies: P4-12. Check: every draft claim includes evidence IDs.
- [ ] **P4-14 — Implement next-steps drafting.** Generate the required assessment, evidence table, gaps, interview themes, questions, study plan, risks, and timing. Dependencies: P4-12. Check: required-section validator.
- [ ] **P4-15 — Render `job-post.md`.** Produce canonical metadata and original description with safe Markdown formatting. Dependencies: P4-08. Check: golden-file test.
- [ ] **P4-16 — Render `cv.tex`.** Fill `TEMPLATE.tex`, preserve moderncv, escape LaTeX, and omit unsupported sections. Dependencies: P4-13. Check: special-character fixture compiles.
- [ ] **P4-17 — Render `next-steps.mdx`.** Render structured next steps without executable MDX components. Dependencies: P4-14. Check: golden-file test.
- [ ] **P4-18 — Add deterministic application validation.** Check dates, language consistency, TODOs, contact policy, source IDs, required files, and LaTeX safety. Dependencies: P4-15 through P4-17. Check: one test per failure category.
- [ ] **P4-19 — Add optional Terra review.** Review the rendered bundle for unsupported claims and recruiter clarity; return findings, not direct edits. Dependencies: P4-18. Check: disabling Terra leaves the Luna workflow functional.
- [ ] **P4-20 — Compile draft artifacts.** Compile in a temporary application directory and attach page count/errors to graph state. Dependencies: P3-17, P4-18. Check: graph node handles success and failure.
- [ ] **P4-21 — Implement final review interrupt.** Show diffs, validation, Terra findings, and PDF before finalization. Dependencies: P4-19, P4-20. Check: reject and revise paths do not write the final folder.
- [ ] **P4-22 — Finalize application atomically.** Create a new dated slug folder only after approval; refuse overwrite and move validated temporary artifacts together. Dependencies: P4-21. Check: duplicate slug fails without partial files.
- [ ] **P4-23 — Wire graph routing.** Compile the nodes, bounded retries, validation loops, interrupts, and terminal states. Dependencies: P4-08 through P4-22. Check: fake-model happy-path graph test.
- [ ] **P4-24 — Stream workflow events.** Add start, inspect, SSE events, and resume endpoints keyed by thread ID. Dependencies: P4-23. Check: API test observes ordered node events.
- [ ] **P4-25 — Build Create CV stepper.** Connect job input, evidence review, generation progress, final review, and completion to the graph API. Dependencies: P4-24, P3-14. Check: browser happy path using fake model responses.
- [ ] **P4-26 — Test restart recovery.** Stop the agent at evidence review, restart it, and resume the same thread without repeating completed nodes. Dependencies: P4-07, P4-24. Check: integration test asserts node call counts.
- [ ] **P4-27 — Workflow safety review.** **Terra review.** Audit evidence provenance, prompt-injection boundaries, retry loops, finalization, and deterministic checks. Dependencies: P4-01 through P4-26. Check: `make test` plus graph integration tests.

## Phase 5 — ADK conversational assistant

- [ ] **P5-01 — Add Google ADK.** Add the Python ADK package only after the LangGraph workflow is stable and record its resolved version. Dependencies: P4-27. Check: import and minimal agent construction test.
- [ ] **P5-02 — Persist ADK sessions.** Configure local SQLite-backed sessions under `.whats-a-cv/` and expose create/get/list operations. Dependencies: P5-01. Check: session survives service restart.
- [ ] **P5-03 — Define shared agent context.** Add selected records, selected application, pending proposal, and active workflow thread IDs. Dependencies: P5-02. Check: context serialization test.
- [ ] **P5-04 — Adapt `list_records`.** Expose the repository read service as a typed ADK tool with documented return and errors. Dependencies: P1-21, P5-01. Check: tool test.
- [ ] **P5-05 — Adapt `read_record`.** Expose one record without leaking unrequested contact values. Dependencies: P1-22, P5-04. Check: contact redaction test.
- [ ] **P5-06 — Adapt `propose_record_change`.** Create proposals only; never approve within the same tool call. Dependencies: P1-25, P5-04. Check: target remains unchanged.
- [ ] **P5-07 — Adapt application reads.** Expose bundle inspection with private notes excluded by default. Dependencies: P3-04, P5-04. Check: notes omission test.
- [ ] **P5-08 — Adapt the LangGraph workflow.** Expose start/status/resume as ADK tools while preserving graph interrupts. Dependencies: P4-24, P5-04. Check: tool starts the same compiled graph used by Create CV.
- [ ] **P5-09 — Add plan-saving tools.** Save approved study and interview plans as dated Markdown through proposals. Dependencies: P1-25, P5-04. Check: no file is written before approval.
- [ ] **P5-10 — Build Profile Curator agent.** Limit it to profile questions and record-change proposals using P5-04 through P5-06. Dependencies: P5-04 through P5-06. Check: eval rejects a direct-write request.
- [ ] **P5-11 — Build Application Coach agent.** Limit it to role assessment, application inspection, and invoking the graph. Dependencies: P5-07, P5-08. Check: “prepare application” returns a workflow thread ID.
- [ ] **P5-12 — Build Learning Coach agent.** Generate focused study/interview plans from explicit gaps and save only on request. Dependencies: P5-09. Check: ordinary advice creates no file proposal.
- [ ] **P5-13 — Build root What's a CV? agent.** Route between the three delegates and keep user-facing approval boundaries explicit. Dependencies: P5-10 through P5-12. Check: routing cases select the expected delegate.
- [ ] **P5-14 — Add chat APIs.** Add session list/detail and message endpoints with typed events. Dependencies: P5-02, P5-13. Check: multi-turn API test.
- [ ] **P5-15 — Stream chat events.** Stream text deltas, tool starts/results, artifacts, errors, and approval requests over SSE. Dependencies: P5-14. Check: event-order contract test.
- [ ] **P5-16 — Build Assistant layout.** Add session sidebar, conversation pane, composer, and empty/error/loading states. Dependencies: P5-14, P2-03. Check: web build and component tests.
- [ ] **P5-17 — Render tool activity.** Show tool name, safe inputs, status, duration, and result summary without secrets. Dependencies: P5-15, P5-16. Check: secret fixture is redacted.
- [ ] **P5-18 — Render proposal approvals.** Show diff plus approve/reject controls and update the conversation after decision. Dependencies: P2-18, P5-17. Check: browser approve/reject test.
- [ ] **P5-19 — Render workflow artifacts.** Link an assistant-started application to the Create CV stepper and final application. Dependencies: P4-25, P5-08, P5-16. Check: one thread is visible in both interfaces.
- [ ] **P5-20 — Add context chips.** Let users attach/detach records or applications and show exactly what context will be sent. Dependencies: P5-03, P5-16. Check: detached context is absent from the API request.
- [ ] **P5-21 — Add conversation compaction.** Summarize old turns only after a threshold while preserving approvals, unresolved questions, and source references. Dependencies: P5-14. Check: long-session test retains pending proposal ID.
- [ ] **P5-22 — Assistant safety review.** **Terra review.** Audit routing, tool scope, approvals, contact redaction, prompt injection, and session isolation. Dependencies: P5-01 through P5-21. Check: assistant integration suite.

## Phase 6 — Hybrid evidence retrieval

- [ ] **P6-01 — Define retrieval benchmark.** Add sanitized queries with expected source files for common skills and role requirements. Dependencies: P4-10. Check: benchmark runs lexical baseline.
- [ ] **P6-02 — Normalize searchable documents.** Convert source records into section-level documents with stable IDs, paths, headings, and content hashes. Dependencies: P1-21. Check: unchanged corpus produces stable IDs.
- [ ] **P6-03 — Improve lexical retrieval.** Add deterministic tokenization, metadata filters, and ranked results over the normalized documents. Dependencies: P6-01, P6-02. Check: benchmark report records recall and precision.
- [ ] **P6-04 — Add Qdrant service.** Add a Compose service and health check with data stored only in a derived volume. Dependencies: P0-12. Check: `docker compose config` and Qdrant health.
- [ ] **P6-05 — Add embedding configuration.** Configure one explicit embedding model and dimensionality without reusing the chat-model setting. Dependencies: P4-02, P6-04. Check: missing-key behavior is clear and lexical search still works.
- [ ] **P6-06 — Build the evidence index.** Upsert normalized documents with hashes and delete stale derived entries. Dependencies: P6-02, P6-04, P6-05. Check: rebuild twice without duplicate points.
- [ ] **P6-07 — Add semantic search.** Query Qdrant and return the same source-backed result shape as lexical search. Dependencies: P6-06. Check: every result resolves to a canonical source.
- [ ] **P6-08 — Fuse lexical and semantic results.** Add one deterministic reciprocal-rank-fusion implementation. Dependencies: P6-03, P6-07. Check: fixed fixture has stable ordering.
- [ ] **P6-09 — Expose index status and rebuild.** Add status/rebuild API with progress and stale detection. Dependencies: P6-06. Check: modifying a fixture marks the index stale.
- [ ] **P6-10 — Add Lab retrieval view.** Show lexical, semantic, and fused results with scores and source excerpts. Dependencies: P6-08, P6-09. Check: UI can run lexical-only when Qdrant is unavailable.
- [ ] **P6-11 — Gate hybrid retrieval.** **Terra review.** Compare hybrid to lexical on P6-01 and enable it by default only if agreed metrics improve. Dependencies: P6-01 through P6-10. Check: committed comparison report and explicit decision.

## Phase 7 — Observability and prompt management

- [ ] **P7-01 — Define telemetry redaction.** Create and test one sanitizer for secrets, contact values, authorization headers, and private notes. Dependencies: P1-19, P3-13. Check: table-driven redaction tests.
- [ ] **P7-02 — Add trace context.** Propagate trace/run/session IDs across web requests, FastAPI, ADK, LangGraph, and tools. Dependencies: P4-24, P5-15. Check: integration test sees one correlated trace ID.
- [ ] **P7-03 — Add OpenTelemetry SDK.** Instrument FastAPI requests and explicit workflow spans with local no-op fallback. Dependencies: P7-01, P7-02. Check: service boots when exporter is absent.
- [ ] **P7-04 — Add local collector.** Add OpenTelemetry Collector to Compose with localhost-only ports. Dependencies: P7-03. Check: collector config validation.
- [ ] **P7-05 — Add Langfuse locally.** Add the documented self-hosted services under a Compose profile and persistent derived volumes. Dependencies: P0-12. Check: Langfuse health endpoint.
- [ ] **P7-06 — Export sanitized traces.** Send spans to Langfuse only after P7-01 redaction. Dependencies: P7-03 through P7-05. Check: seeded secret is absent from exported trace data.
- [ ] **P7-07 — Name stable spans.** Add stable spans for agent, graph node, model, retrieval, tool, approval, and compilation operations. Dependencies: P7-06. Check: one fake application trace contains every expected span class.
- [ ] **P7-08 — Record model usage.** Capture model ID, prompt version, input/cached/output/reasoning tokens, latency, and estimated cost. Dependencies: P4-03, P7-07. Check: fake usage object maps correctly.
- [ ] **P7-09 — Version prompts.** Move model prompts into named, versioned files or Langfuse-backed templates with a local fallback. Dependencies: P7-08. Check: trace links to an exact prompt version.
- [ ] **P7-10 — Add Lab trace links.** Link runs and chat sessions to their local Langfuse trace pages and show a privacy-safe summary. Dependencies: P7-06, P5-16. Check: missing Langfuse shows a disabled state.
- [ ] **P7-11 — Observability review.** **Terra review.** Trace one full application and verify usefulness, stable naming, redaction, and failure visibility. Dependencies: P7-01 through P7-10. Check: signed-off trace checklist.

## Phase 8 — Evaluations and model comparison

- [ ] **P8-01 — Define evaluation schema.** Model input job, allowed evidence, expected requirements, expected gaps, forbidden claims, and output language. Dependencies: P4-05. Check: schema validates one minimal case.
- [ ] **P8-02 — Add sanitized baseline cases.** Commit at least five job cases with no private contact details and explicit expectations. Dependencies: P8-01. Check: privacy scan and schema validation.
- [ ] **P8-03 — Grade requirement extraction.** Calculate must-have/preferred precision and recall against expected IDs or normalized text. Dependencies: P4-09, P8-02. Check: deterministic grader unit tests.
- [ ] **P8-04 — Grade evidence matching.** Calculate source-level precision/recall and count unresolved gaps. Dependencies: P4-11, P8-02. Check: deterministic grader unit tests.
- [ ] **P8-05 — Grade unsupported claims.** Fail any CV claim without an allowed evidence ID. Dependencies: P4-13, P8-02. Check: one invented-claim fixture fails.
- [ ] **P8-06 — Grade artifact validity.** Score required files, output language, LaTeX compilation, page limit, sections, and TODO policy. Dependencies: P4-18, P8-02. Check: good and bad bundle fixtures.
- [ ] **P8-07 — Build evaluation runner.** Run selected cases/models/prompts, isolate outputs, and emit JSON plus Markdown reports. Dependencies: P8-03 through P8-06. Check: one-case fake-model run.
- [ ] **P8-08 — Add `make eval`.** Run the baseline dataset and write reports outside canonical data. Dependencies: P8-07. Check: `make eval` returns nonzero on a failed release gate.
- [ ] **P8-09 — Integrate ADK evaluations.** Express assistant routing/tool-use cases in ADK's supported evaluation format. Dependencies: P5-22, P8-02. Check: profile-change and application-start cases pass.
- [ ] **P8-10 — Integrate Langfuse experiments.** Upload/run sanitized cases with prompt and model versions attached. Dependencies: P7-09, P8-07. Check: one experiment result links to its trace.
- [ ] **P8-11 — Compare Luna-only and Luna-plus-Terra.** Run the same cases and report quality, latency, tokens, and cost. Dependencies: P4-19, P8-08. Check: committed dated comparison report.
- [ ] **P8-12 — Decide production routing.** **Terra review.** Keep Terra review only for metrics it measurably improves; document thresholds and fallback behavior. Dependencies: P8-11. Check: configuration matches the written decision.
- [ ] **P8-13 — Add CI evaluation smoke test.** Run deterministic graders and one fake-model graph case on every change; keep paid live-model evals manual. Dependencies: P8-08. Check: local CI command passes without API keys.
- [ ] **P8-14 — Add evaluation Lab view.** Select cases/configurations and display reports without making the browser responsible for grading. Dependencies: P8-07, P2-03. Check: existing report renders with no model key.

## Phase 9 — Hardening and portfolio delivery

- [ ] **P9-01 — Add backup command.** Copy only canonical Markdown and application artifacts into a timestamped archive without secrets from derived state. Dependencies: P3-20. Check: restore archive into a temporary directory and validate it.
- [ ] **P9-02 — Add recovery documentation.** Document deleting/rebuilding SQLite, Qdrant, caches, and observability while preserving canonical files. Dependencies: P6-09, P7-05. Check: perform recovery on a temporary clone.
- [ ] **P9-03 — Write threat model.** Cover job-post prompt injection, SSRF, path traversal, symlinks, command injection, telemetry leakage, stale approvals, and malicious Markdown/LaTeX. Dependencies: P4-27, P5-22, P7-11. Check: every threat maps to a control or tracked gap.
- [ ] **P9-04 — Add dependency scanning.** Add lockfile-aware Python and npm vulnerability checks to CI with documented exception handling. Dependencies: P0-06, P0-09. Check: local scan commands run.
- [ ] **P9-05 — Add secret scanning.** Scan commits and the working tree for provider keys and private demo values. Dependencies: P0-02. Check: seeded fake secret is detected.
- [ ] **P9-06 — Add demo profile.** Create a clearly fictional, isolated dataset for screenshots and demos without copying candidate facts. Dependencies: P2-22. Check: demo mode never reads `contact/` or real applications.
- [ ] **P9-07 — Add critical browser suite.** Cover profile edit, application generation, past artifact viewing, and rejected assistant proposal. Dependencies: P2-22, P4-25, P5-18. Check: Playwright suite passes against Compose.
- [ ] **P9-08 — Verify one-command fresh start.** Test `make dev` from a fresh clone with Docker available and no provider key. Dependencies: all prior implementation phases. Check: UI/profile/application history load and AI controls explain configuration.
- [ ] **P9-09 — Measure local resource use.** Record idle and active CPU, memory, startup time, and disk usage for the full profile; document a lighter core profile if needed. Dependencies: P7-05, P9-08. Check: reproducible measurement notes.
- [ ] **P9-10 — Create architecture diagram.** Document runtime services, canonical/derived storage, agent handoffs, approvals, and telemetry flow. Dependencies: P8-12. Check: diagram matches Compose and code paths.
- [ ] **P9-11 — Document engineering decisions.** Index ADRs and explain why each industry tool has a real responsibility. Dependencies: P0-03 through P0-05, P9-10. Check: no tool in Compose is absent from the responsibility table.
- [ ] **P9-12 — Produce demo evidence.** Capture privacy-safe screenshots or a short recording of the four primary workflows plus Lab tracing/evals. Dependencies: P6-10, P7-10, P8-14, P9-06. Check: manually verify no real contact value appears.
- [ ] **P9-13 — Record measured project evidence.** Add a project record only with technologies, outcomes, metrics, and capabilities actually implemented and measured. Dependencies: P8-11, P9-09, P9-12. Check: every claim links to code, report, or artifact.
- [ ] **P9-14 — Final product audit.** **Terra review.** Audit `AGENTS.md`, `BUILD_PLAN.md`, completed tasks, privacy, tests, evals, startup, recovery, and truthful portfolio evidence. Dependencies: P9-01 through P9-13. Check: `make test`, `make eval`, Playwright, and fresh-start checks pass.

## Deferred task seeds

Do not split these into implementation tasks until P9-14 is complete and actual usage justifies them:

- Cloud deployment
- Native desktop wrapper
- Browser extension
- Automatic job submission
- Email/calendar integrations
- Multiple users and permissions
- Cloud synchronization
- Voice interaction
- Autonomous background agents
- Fine-tuning
- Kubernetes deployment
