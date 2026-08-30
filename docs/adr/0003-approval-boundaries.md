# ADR 0003: Approval boundaries protect canonical data

- Status: Accepted
- Date: 2026-08-30

## Decision

Agents do not receive direct filesystem access. They may use only typed tools
provided by the repository service, which enforces approved roots, paths, and
extensions.

## Action classes

| Class | Allowed actions | Approval |
| --- | --- | --- |
| Read | List records, read records or applications, search evidence, and inspect saved artifacts | Immediate |
| Proposal | Validate a requested change, generate a diff, and create a pending record, plan, status, or note proposal | Immediate; must not change the target |
| Canonical write | Approve a pending proposal and apply it atomically to a Markdown record or application metadata | Explicit user approval after reviewing the diff |
| Application finalization | Compile and save a new application bundle or generated deliverable | Explicit user approval after validation, diff, and PDF review |
| Destructive or external action | Delete or clean derived state, overwrite existing output, run compilation commands, or fetch external content | Explicit approval for the specific action |

Proposal tools cannot approve their own changes. Approval must verify that the
proposal is still pending and that the target has not changed since the
proposal was created. Rejected proposals leave canonical files unchanged.

Destructive actions are limited to documented, rebuildable derived state and
must never remove canonical Markdown, contact records, completed applications,
or Git history. Existing application folders are never overwritten without
explicit approval.

## Consequences

The UI and assistant can show reviewable diffs and approval requests without
silently mutating candidate data. The repository service is the only boundary
for reads and writes, making path validation, atomic writes, contact privacy,
and stale-proposal checks enforceable in one place.
