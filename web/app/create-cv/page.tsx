"use client";

import { useState } from "react";

const slugify = (value: string) => value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export default function CreateCvPage() {
  const [name, setName] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [message, setMessage] = useState("");
  const slug = slugify(name);
  const create = async () => {
    const response = await fetch("/api/proposals", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_path: `projects/${slug}.md`, proposed_content: `---\nname: ${JSON.stringify(name)}\nrole: \"\"\nurl: \"\"\nstart: \"\"\nend: present\n---\n\n# ${name}\n` }) });
    setMessage(response.ok ? "Creation proposal submitted for review." : "Could not create proposal.");
  };
  return <section className="form-page"><h1>Add a project</h1><p className="lede">Add a project to the evidence you can draw on for future applications.</p>
    <form className="create-record-form" onSubmit={(event) => { event.preventDefault(); void create(); }}>
      <label>Project name<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
      <p className="field-hint">It will be saved as <code>{slug || "a-project-name"}</code>.</p>
      <label className="checkbox-label"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} required /> I&apos;ve checked the project name</label>
      <button className="button button-primary" type="submit" disabled={!confirmed || !slug}>Create proposal</button>
      {message && <p role="status">{message}</p>}
    </form>
  </section>;
}
