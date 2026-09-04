---
name: product-ux-review
description: Review and improve the What's a CV? web UX end to end. Use for full product reviews and requests involving usability, navigation, accessibility, responsive layout, workflow feedback, profile relationships, application management, or frontend polish. Do not use for CV-writing-only tasks.
---

# Product UX review

Preserve the candidate-first, local-first product described in `PRODUCT.md` and the visual language in `DESIGN.md`. Read `web/AGENTS.md` before changing Next.js code.

## Work end to end

- Trace each affected interaction through the React page, Next.js route, FastAPI endpoint, repository function, and existing tests before editing.
- Reuse existing tokens, controls, data models, and shared functions. Prefer a fix at the shared boundary over duplicated UI workarounds.
- Keep canonical Markdown records truthful and unchanged unless the user explicitly asks to edit career data.
- Make relationships navigable in both directions when the underlying source data supports them.

## UX floor

- Preserve clear heading order, visible focus, labelled controls, 44px touch targets, keyboard navigation, and responsive layouts.
- Include useful loading, error, empty, success, and disabled states for affected workflows.
- Show progress for multi-step or long-running work using native semantic elements when practical.
- Separate unfinished work from completed work. Destructive actions require clear selection, confirmation, actionable failure feedback, and server-side scope enforcement.
- Use plain candidate-facing language; avoid developer terminology and decorative UI that does not help complete the task.

## Verification

Run the smallest relevant backend tests, `npm run lint`, `npm run build`, and the Impeccable detector over changed UI files. Inspect the rendered desktop and mobile flows once when the local browser environment is available. Report any check blocked by the environment rather than implying it passed.
