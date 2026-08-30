---
name: What's a CV?
description: A calm, candidate-first workspace for maintaining career evidence and preparing tailored applications.
colors:
  background: "#f8f7f4"
  surface: "#fffefa"
  surface-muted: "#f1f4f8"
  border: "#d9dfe8"
  border-strong: "#aeb9c9"
  ink: "#15223a"
  ink-muted: "#5a687c"
  primary: "#1559d6"
  primary-hover: "#0e46ae"
  primary-active-surface: "#eaf1ff"
  primary-active-border: "#aecaff"
  success: "#16704a"
  success-surface: "#e4f6ed"
  privacy-surface: "#edf8f1"
  privacy-ink: "#215d43"
  editor-surface: "#f3f5f8"
typography:
  display:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(2rem, 5vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 650
    lineHeight: 1.5
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  pill: "999px"
spacing:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  5: "20px"
  6: "24px"
  8: "32px"
  10: "40px"
  12: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "10px 16px"
    height: "44px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "10px 16px"
    height: "44px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "8px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "24px"
---

# Design System: What's a CV?

## Overview

**Creative North Star: "The Candidate's Writing Desk"**

What's a CV? is a calm, practical workspace rather than developer tooling. It uses warm paper-like surfaces, strong editorial headings, and precise blue actions to make a candidate's career history feel valuable, organized, and approachable.

The design favors clear structure over decorative chrome. A persistent sidebar makes the workspace predictable; generous page spacing reduces cognitive load; bordered summaries, forms, and previews give dense career information a stable place to live. Privacy and local ownership are communicated quietly with restrained mint states, never alarmist messaging.

**Key Characteristics:**

- Warm off-white canvas with deep navy ink and a single cobalt action color.
- Georgia display headings paired with a neutral system sans for readable controls and body copy.
- Thin borders and tonal surface changes establish hierarchy; shadows are reserved for hover feedback.
- Forms use labelled fields in compact grids; record facts use a definition-list table.
- Mobile turns the sidebar into a scrollable navigation row and stacks multi-column panels.

## Colors

The palette is a quiet writing environment: warm neutrals carry most of the interface, cobalt communicates action and selection, and mint communicates privacy or successful status.

### Primary

- **Cobalt action** (`{colors.primary}` — #1559d6): primary calls to action, selected navigation, links, focus treatment, and checkbox accents.
- **Deep cobalt** (`{colors.primary-hover}` — #0e46ae): hover and active state for primary actions.
- **Pale blue selection** (`{colors.primary-active-surface}` — #eaf1ff): selected tabs and navigation hover.

### Neutral

- **Warm canvas** (`{colors.background}` — #f8f7f4): page background.
- **Writing surface** (`{colors.surface}` — #fffefa): panels, forms, navigation, inputs, and summary tables.
- **Cool editor surface** (`{colors.editor-surface}` — #f3f5f8): Markdown source and code-like content only.
- **Ink** (`{colors.ink}` — #15223a): headings, labels, and high-emphasis text.
- **Muted ink** (`{colors.ink-muted}` — #5a687c): helper copy, source paths, and secondary information.
- **Hairline border** (`{colors.border}` — #d9dfe8): panel, table-row, and layout dividers.

### Status

- **Local-green** (`{colors.success}` / `{colors.success-surface}` — #16704a / #e4f6ed): quiet positive or local-state confirmations.
- **Privacy wash** (`{colors.privacy-surface}` / `{colors.privacy-ink}` — #edf8f1 / #215d43): ownership and privacy callouts.

**The One Accent Rule.** Cobalt is reserved for action, selection, links, and focus. It is not a large background fill or decorative treatment.

## Typography

**Display Font:** Georgia, with Times New Roman fallback.

**Body Font:** Inter, ui-sans-serif, system-ui, sans-serif.

**Character:** Editorial display type gives career narratives appropriate gravity; the compact sans keeps workflows, labels, and data easy to scan.

### Hierarchy

- **Display** (700, `clamp(2rem, 5vw, 3rem)`, 1.2): page titles and welcome messages; max measure is 18ch.
- **Title** (700, 1.5rem, 1.2): panel and section headings.
- **Body** (400, 1rem, 1.5): default prose and field values.
- **Lead** (400, 1.125rem, 1.65): introductory copy; keep to roughly 62ch.
- **Label** (650, 0.875rem, 1.5): form labels, summary keys, navigation, and action text.
- **Code / source** (400, 0.875rem, 1.65): system monospace is reserved for Markdown previews and source-like text.

## Layout

The desktop workspace uses a 17rem sidebar beside fluid content. Main content is capped at 72rem and uses 48–96px of page padding. Within a page, related controls sit close together while major sections separate with 32–48px of space.

The editor is a 1.15fr / 0.85fr grid: an editable form panel on the left and a sticky live preview on the right. Record facts use a labelled two-column definition-list table. At 48rem and below, the app shell becomes one column, navigation scrolls horizontally, all form grids collapse to one column, and the preview follows the form in normal document flow.

## Elevation & Depth

The system is flat by default. Panels use a white surface plus a 1px border; depth comes from spacing and tonal contrast. Only record cards lift on hover with `0 12px 28px rgb(31 57 97 / 8%)`. Motion is short (160ms, ease-out) and limited to background, border, color, and a 1px action lift. The welcome panel may use one gentle 520ms entrance; reduced-motion preferences disable it.

## Shapes

Functional controls use 8px corners. Panels, tables, record cards, and editor regions use 12px corners. Larger containers may use 16px corners. Pills are reserved for small statuses and counters, never primary workflow controls. Borders are always 1px and neutral.

## Components

### Buttons

- **Primary:** cobalt fill, white 700 label, 44px minimum height, 8px radius. Hover darkens the fill and lifts 1px.
- **Secondary:** warm surface, neutral border, ink label. Hover uses cobalt border and text; it remains visually quieter than primary.
- **Disabled:** reduce opacity to 0.55 and remove the lift.

### Inputs and Fields

- Inputs and textareas use a warm surface, 1px strong-neutral border, 8px radius, and inherited body type.
- Labels appear directly above controls in 700-weight sans type.
- Related fields use a two-column grid on desktop and a single column on mobile.
- Preserve visible cobalt keyboard focus with a 2px outline and pale blue ring.

### Panels and Record Tables

- Panels use a warm white surface, 1px neutral border, 12px radius, and 20–24px internal padding.
- Record details use a definition-list table: muted 0.875rem keys and stronger values, divided by hairlines.
- Markdown source stays inside the cool editor surface; live preview uses the surrounding panel and no nested border.

### Navigation

- The sidebar is quiet but persistent: serif wordmark, semibold sans navigation, no icons required.
- Hover and selected navigation use pale blue surface with cobalt text.
- On mobile, navigation becomes a horizontally scrollable row; hide the status chip rather than crowding the header.

### Status and Privacy

- Status chips are compact rounded pills with mint surface, border, and text.
- Privacy messages use a larger mint panel and plain-language ownership copy.

## Do's and Don'ts

### Do:

- **Do** use warm surfaces and precise hairlines to group information before reaching for shadows.
- **Do** use the serif display face only for page-level narrative or high-level headings.
- **Do** make editing explicit: labelled fields, a clear review action, and a live preview beside or below it.
- **Do** use cobalt only where the candidate can act, select, or navigate.
- **Do** preserve readable, stacked editing on screens at or below 48rem.

### Don't:

- **Don't** use the old black-and-white Vercel aesthetic, mesh gradients, technical eyebrows, or marketing pills.
- **Don't** let record facts float as ungrouped label/value text; use the structured definition-list table.
- **Don't** nest bordered panels inside bordered panels unless the inner surface is a distinct editor or source view.
- **Don't** add visual-only icons, charts, progress rings, or decorative illustrations to routine career-management tasks.
