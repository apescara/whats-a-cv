# What's a CV?

A local-first workspace for maintaining one career source of truth and adapting it to each opportunity. The experience is the durable asset; a CV is only one temporary, job-specific view of it.

## Set up your profile

Copy the `_template.md` file in each folder and create one file per real item. Start with:

1. `contact/`
2. `experience/`
3. `education/`
4. `expertise/` and `languages/`
5. `certifications/` and `projects/` when relevant

Keep claims factual and add outcomes, scale, and metrics to experience files whenever you can verify them. Expertise records are most persuasive when their `Evidence` section points to a role, achievement, or project.

Fill in `preferences.md` to help evaluate opportunities. It is planning context and is not copied into a CV automatically.

## Tailor an application

Give the agent the job description or URL and, optionally, the desired language. For example:

> Prepare my application for this Senior Platform Engineer role: https://example.com/job. Write it in English.

The agent creates:

```text
applications/YYYY-MM-DD-company-role/
├── job-post.md       # Saved source posting and metadata
├── cv.tex            # Tailored moderncv document
└── next-steps.mdx    # Fit analysis and preparation plan
```

Review every claim and resolve any `TODO` before applying. If `latexmk` and `moderncv` are installed, compile with:

```sh
tlmgr install moderncv # one-time setup when moderncv is missing
latexmk -pdf applications/YYYY-MM-DD-company-role/cv.tex
```

## Privacy

Personal files under `contact/` are ignored by Git by default; `_template.md` remains tracked. Check repository visibility and staged files before committing any personal information.
