"use client";

import { useState } from "react";

type RecordData = { [key: string]: unknown };
type Field = { name: string; label: string; type?: "text" | "date" };

const experienceFields: Field[] = [
  { name: "company", label: "Company" }, { name: "role", label: "Role" },
  { name: "employment_type", label: "Employment type" }, { name: "location", label: "Location" },
  { name: "start", label: "Start", type: "date" }, { name: "end", label: "End", type: "date" },
];
const educationFields: Field[] = [
  { name: "institution", label: "Institution" }, { name: "qualification", label: "Qualification" },
  { name: "field", label: "Field" }, { name: "location", label: "Location" },
  { name: "start", label: "Start", type: "date" }, { name: "end", label: "End", type: "date" },
];
const certificationFields: Field[] = [
  { name: "name", label: "Name" }, { name: "issuer", label: "Issuer" },
  { name: "issued", label: "Issued", type: "date" }, { name: "expires", label: "Expires", type: "date" },
  { name: "credential_id", label: "Credential ID" }, { name: "url", label: "URL" },
];
const projectFields: Field[] = [
  { name: "name", label: "Name" }, { name: "role", label: "Role" }, { name: "url", label: "URL" },
  { name: "start", label: "Start", type: "date" }, { name: "end", label: "End", type: "date" },
];
const expertiseFields: Field[] = [
  { name: "name", label: "Name" }, { name: "category", label: "Category" }, { name: "last_used", label: "Last used", type: "date" },
  { name: "evidence", label: "Evidence (JSON)" },
];
const languageFields: Field[] = [
  { name: "language", label: "Language" }, { name: "proficiency", label: "Proficiency" }, { name: "certification", label: "Certification" },
];

function markdown(values: RecordData, recordFields: Field[]) {
  const header = recordFields.map(({ name }) => `${name}: ${JSON.stringify(values[name] || "")}`).join("\n");
  return `---\n${header}\n---\n${String(values.body || "")}`;
}

export default function RecordEditor({ record, kind }: { record: RecordData; kind: "experience" | "education" | "certifications" | "projects" | "expertise" | "languages" }) {
  const recordFields = kind === "education" ? educationFields : kind === "certifications" ? certificationFields : kind === "projects" ? projectFields : kind === "expertise" ? expertiseFields : kind === "languages" ? languageFields : experienceFields;
  const [values, setValues] = useState(record);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [diff, setDiff] = useState("");
  const [proposalId, setProposalId] = useState<number | null>(null);

  const update = (name: string, value: string) => setValues((current) => ({ ...current, [name]: name === "evidence" ? (() => { try { return JSON.parse(value); } catch { return value; } })() : value }));
  const submit = async () => {
    setError("");
    setMessage("");
    const response = await fetch("/api/proposals", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_path: `${kind}/${String(record.slug)}.md`, proposed_content: markdown(values, recordFields) }) });
    if (!response.ok) { setError("Could not create a proposal. Check your connection and try again."); return; }
    const { id } = await response.json() as { id: number };
    setProposalId(id);
    const review = await fetch(`/api/proposals/${id}`);
    const proposal = await review.json() as { diff?: string };
    setDiff(proposal.diff || "No changes.");
    setMessage("Proposal ready for review.");
  };
  const decide = async (action: "approve" | "reject") => {
    if (proposalId === null) return;
    const response = await fetch(`/api/proposals/${proposalId}/${action}`, { method: "POST" });
    setMessage(response.ok ? `Proposal ${action}d.` : `Could not ${action} proposal.`);
    if (response.ok) window.location.reload();
  };

  return <form className="record-editor" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
    <section className="record-editor-fields">
      <div className="editor-heading"><h2>Edit {kind}</h2><p>Review your changes before they are saved.</p></div>
      <div className="editor-field-grid">
        {recordFields.map(({ name, label, type }) => <label key={name}>{label}<input name={name} autoComplete="off" type={type || "text"} value={name === "evidence" ? JSON.stringify(values[name] || []) : String(values[name] || "")} onChange={(event) => update(name, event.target.value)} /></label>)}
      </div>
      <label className="editor-details">Markdown details<textarea rows={10} value={String(values.body || "")} onChange={(event) => update("body", event.target.value)} /></label>
      <div className="editor-actions"><button type="submit">Review changes</button></div>
      {error && <p role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      {diff && <pre className="markdown-preview" aria-label="Proposal diff">{diff}</pre>}
      {proposalId !== null && <div className="editor-actions"><button type="button" onClick={() => void decide("approve")}>Approve</button> <button className="button-secondary" type="button" onClick={() => void decide("reject")}>Reject</button></div>}
    </section>
    <aside className="editor-preview" aria-label="Live Markdown preview"><h2>Live preview</h2><p>How this record will be stored.</p><pre className="markdown-preview">{markdown(values, recordFields)}</pre></aside>
  </form>;
}

export function ContactEditor({ record }: { record: RecordData }) {
  const [revealed, setRevealed] = useState(false);
  return <section className="record-editor" aria-labelledby="contact-editor-title">
    <h2 id="contact-editor-title">Private contact</h2>
    <p>Inclusion: {record.include_by_default ? "Included by default" : "Not included by default"}</p>
    <p>{revealed ? String(record.value || "") : "••••••••"}</p>
    <button type="button" onClick={() => setRevealed((value) => !value)}>{revealed ? "Hide value" : "Reveal value"}</button>
  </section>;
}
