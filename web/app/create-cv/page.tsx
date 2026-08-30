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
  return <section><h1>Create CV</h1><p>Turn a job post into a targeted application.</p>
    <form className="record-editor" onSubmit={(event) => { event.preventDefault(); void create(); }}>
      <label>Project or record name<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
      <p>Suggested slug: <code>{slug || "—"}</code></p>
      <label><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} required /> Confirm this slug</label>
      <button type="submit" disabled={!confirmed || !slug}>Create proposal</button>
      {message && <p role="status">{message}</p>}
    </form>
  </section>;
}
