"use client";

import { useState } from "react";

type RecordData = { [key: string]: unknown };
type Field = { name: string; label: string; type?: "text" | "date" };

const fields: Field[] = [
  { name: "company", label: "Company" }, { name: "role", label: "Role" },
  { name: "employment_type", label: "Employment type" }, { name: "location", label: "Location" },
  { name: "start", label: "Start", type: "date" }, { name: "end", label: "End", type: "date" },
];

function markdown(values: RecordData) {
  const header = fields.map(({ name }) => `${name}: ${JSON.stringify(values[name] || "")}`).join("\n");
  return `---\n${header}\n---\n${String(values.body || "")}`;
}

export default function ExperienceEditor({ record }: { record: RecordData }) {
  const [values, setValues] = useState(record);
  const [message, setMessage] = useState("");

  const update = (name: string, value: string) => setValues((current) => ({ ...current, [name]: value }));
  const submit = async () => {
    const response = await fetch("/api/proposals", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_path: `experience/${String(record.slug)}.md`, proposed_content: markdown(values) }) });
    setMessage(response.ok ? "Proposal created for review." : "Could not create proposal.");
  };

  return <form className="record-editor" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
    <h2>Edit experience</h2>
    {fields.map(({ name, label, type }) => <label key={name}>{label}<input type={type || "text"} value={String(values[name] || "")} onChange={(event) => update(name, event.target.value)} /></label>)}
    <label>Markdown details<textarea rows={10} value={String(values.body || "")} onChange={(event) => update("body", event.target.value)} /></label>
    <button type="submit">Submit proposal</button>
    {message && <p role="status">{message}</p>}
  </form>;
}
