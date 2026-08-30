# ADR 0002: Separate conversation from application workflow

- Status: Accepted
- Date: 2026-08-30

## Decision

The system assigns one orchestration responsibility to each tool:

| Tool | Owner responsibility |
| --- | --- |
| Google ADK | Open-ended conversation, sessions, routing, tools, and artifacts |
| LangGraph | The durable, resumable CV application workflow, including checkpoints, branching, retries, and human review |
| LangChain | Model integrations, structured outputs, documents, retrievers, and shared integration conventions |

ADK invokes the compiled LangGraph application workflow as a tool when a
conversation starts or resumes CV creation. LangChain supplies integrations
to both layers but does not own routing or the application workflow.

## Workflow boundary

The assistant may discuss profile records, jobs, applications, interviews, and
study plans through ADK. A request to create or revise an application hands off
to LangGraph, which owns the ordered application states through final review.
There is one CV workflow: the LangGraph workflow. ADK must not implement a
second CV-generation path, and LangChain must not become an alternative
orchestrator.

## Consequences

Conversation state and application checkpoints remain distinct. Workflow
retries, approvals, and resumptions are implemented once in LangGraph. Model
and document integration code is shared through LangChain, while user-facing
conversation and tool routing stay in ADK.
