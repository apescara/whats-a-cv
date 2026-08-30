# ADR 0001: Markdown is canonical

- Status: Accepted
- Date: 2026-08-30

## Decision

The repository's Markdown files are the canonical candidate database and the
portable source of truth. The approved canonical roots are:

- `contact/`
- `experience/`
- `education/`
- `certifications/`
- `projects/`
- `expertise/`
- `languages/`
- `preferences.md`
- `applications/`
- `study-plans/`
- `interview-plans/`

Generated CVs, PDFs, job-post snapshots, and preparation artifacts remain
readable files, but they are projections or outputs of the canonical records;
they do not replace those records as the source of candidate facts.

## Derived state boundary

`.whats-a-cv/` is rebuildable local state only:

- `state.db` stores sessions, checkpoints, and application UI state.
- `index/` stores rebuildable index metadata.
- `cache/` stores fetched pages and temporary generation output.
- `logs/` stores local development logs.

Derived state must not be required to recover candidate facts or completed
applications. Removing `.whats-a-cv/` must leave all canonical records and
application deliverables intact.

## Consequences

The application reads and writes canonical Markdown through the repository
service, with validation, atomic writes, diffs, and approval where required.
Indexes, sessions, caches, logs, and other local databases can be deleted and
rebuilt without data loss. Every generated claim must remain traceable to a
canonical source record.
