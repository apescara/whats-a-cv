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

function markdown(values: RecordData, recordFields: Field[]) {
  const header = recordFields.map(({ name }) => `${name}: ${JSON.stringify(values[name] || "")}`).join("\n");
  return `---\n${header}\n---\n${String(values.body || "")}`;
}

export default function RecordEditor({ record, kind }: { record: RecordData; kind: "experience" | "education" | "certifications" }) {
  const recordFields = kind === "education" ? educationFields : kind === "certifications" ? certificationFields : experienceFields;
  const [values, setValues] = useState(record);
  const [message, setMessage] = useState("");

  const update = (name: string, value: string) => setValues((current) => ({ ...current, [name]: value }));
  const submit = async () => {
    const response = await fetch("/api/proposals", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_path: `${kind}/${String(record.slug)}.md`, proposed_content: markdown(values, recordFields) }) });
    setMessage(response.ok ? "Proposal created for review." : "Could not create proposal.");
  };

  return <form className="record-editor" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
    <h2>Edit {kind}</h2>
    {recordFields.map(({ name, label, type }) => <label key={name}>{label}<input type={type || "text"} value={String(values[name] || "")} onChange={(event) => update(name, event.target.value)} /></label>)}
    <label>Markdown details<textarea rows={10} value={String(values.body || "")} onChange={(event) => update("body", event.target.value)} /></label>
    <button type="submit">Submit proposal</button>
    {message && <p role="status">{message}</p>}
  </form>;
}
