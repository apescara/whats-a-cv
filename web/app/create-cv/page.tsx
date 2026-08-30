"use client";

import { useEffect, useState } from "react";

type Draft = { text: string; company: string; role: string; location: string; language: string; source_url: string; retrieved: string };
const emptyDraft: Draft = { text: "", company: "", role: "", location: "", language: "", source_url: "", retrieved: "" };

export default function CreateCvPage() {
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [message, setMessage] = useState("");
  useEffect(() => { try { const saved = sessionStorage.getItem("job-draft"); if (saved) setDraft({ ...emptyDraft, ...JSON.parse(saved) }); } catch { /* Ignore malformed browser-only draft state. */ } }, []);
  const update = (key: keyof Draft, value: string) => setDraft((current) => { const next = { ...current, [key]: value }; sessionStorage.setItem("job-draft", JSON.stringify(next)); return next; });
  const fetchUrl = async () => { const response = await fetch("/api/job-url", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: draft.source_url }) }); const result = await response.json(); if (!response.ok) { setMessage(result.detail || "Could not fetch this URL."); return; } setDraft((current) => { const next = { ...current, text: result.text, retrieved: result.retrieved }; sessionStorage.setItem("job-draft", JSON.stringify(next)); return next; }); setMessage("Job text fetched. Review it before continuing."); };
  return <section className="form-page"><h1>Start an application</h1><p className="lede">Paste a job post or fetch a public URL. This creates a draft only; no application folder is written.</p>
    <form className="create-record-form" onSubmit={(event) => { event.preventDefault(); setMessage(draft.text.trim() ? "Draft saved in this browser session." : "Paste the job description first."); }}>
      <label>Job post text<textarea rows={10} value={draft.text} onChange={(event) => update("text", event.target.value)} required /></label>
      <label>Public job URL<input type="url" value={draft.source_url} onChange={(event) => update("source_url", event.target.value)} placeholder="https://…" /></label>
      <button className="button button-secondary" type="button" onClick={() => void fetchUrl()} disabled={!draft.source_url}>Fetch URL</button>
      <div className="editor-field-grid"><label>Company<input value={draft.company} onChange={(event) => update("company", event.target.value)} required /></label><label>Role<input value={draft.role} onChange={(event) => update("role", event.target.value)} required /></label><label>Location<input value={draft.location} onChange={(event) => update("location", event.target.value)} /></label><label>Language<input value={draft.language} onChange={(event) => update("language", event.target.value)} /></label></div>
      <button className="button button-primary" type="submit">Build application</button>{message && <p role="status">{message}</p>}
    </form>
  </section>;
}
