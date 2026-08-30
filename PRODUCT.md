# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Individual job candidates maintaining a complete, truthful career history. They may not be technical or power users and need a clear, friendly way to prepare applications without wrestling with CV formatting or tailoring.

## Product Purpose

What's a CV? gives candidates control of their complete work history while taking the pain out of creating a tailored CV for each opportunity. Success is a truthful, relevant, reviewable application that the candidate can confidently use.

## Positioning

The candidate owns one local-first Markdown source of truth for their career; the app turns it into job-specific CV applications instead of asking them to repeatedly rewrite their history.

## Operating Context

Candidates build and maintain profile records for contact details, experience, education, expertise, languages, certifications, and projects. For each job posting, the app creates a dated application folder containing the saved posting, a tailored editable LaTeX CV, and concrete preparation next steps.

## Capabilities and Constraints

- Markdown files in the repository are canonical career data.
- The web interface supports profile records, preferences, application creation, and AI-assisted actions.
- AI-proposed changes remain reviewable before acceptance.
- Provider credentials are optional for the non-AI profile experience.
- Claims must remain factual and traceable to source records; unsupported requirements become gaps or TODOs, not CV content.

## Brand Commitments

- Friendly and approachable for people beyond power and technical users.
- Give candidates control rather than hiding or replacing their career history.
- Reduce the stress and effort of preparing a CV.

## Evidence on Hand

- Canonical candidate records and templates: `contact/`, `experience/`, `education/`, `expertise/`, `languages/`, `certifications/`, and `projects/`.
- Application deliverables: `applications/YYYY-MM-DD-company-role/`.
- Existing web implementation: `web/`.
- No customer testimonials, benchmarks, or external proof assets are established in the repository.

## Product Principles

- Career data belongs to the candidate and stays complete, factual, and reusable.
- Tailoring should save work without obscuring the candidate's control.
- Every application should be specific to its role, concise, and easy to review.
- The product should be understandable without specialist knowledge.

