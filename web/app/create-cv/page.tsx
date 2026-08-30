"use client";

import { useEffect, useState } from "react";

type Draft = { text: string; company: string; role: string; location: string; language: string; source_url: string; retrieved: string };
const emptyDraft: Draft = { text: "", company: "", role: "", location: "", language: "", source_url: "", retrieved: "" };

export default function CreateCvPage() {
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [message, setMessage] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<{ requirement_id: string; source_path: string; excerpt: string; confidence: number }[]>([]);
  const [step, setStep] = useState(1);
  useEffect(() => { try { const saved = sessionStorage.getItem("job-draft"); if (saved) setDraft({ ...emptyDraft, ...JSON.parse(saved) }); } catch { /* Ignore malformed browser-only draft state. */ } }, []);
  const update = (key: keyof Draft, value: string) => setDraft((current) => { const next = { ...current, [key]: value }; sessionStorage.setItem("job-draft", JSON.stringify(next)); return next; });
  const fetchUrl = async () => { const response = await fetch("/api/job-url", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: draft.source_url }) }); const result = await response.json(); if (!response.ok) { setMessage(result.detail || "Could not fetch this URL."); return; } setDraft((current) => { const next = { ...current, text: result.text, retrieved: result.retrieved }; sessionStorage.setItem("job-draft", JSON.stringify(next)); return next; }); setMessage("Job text fetched. Review it before continuing."); };
  const startWorkflow = async () => { const response = await fetch("/api/workflow/start", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: draft.text, metadata: { company: draft.company, role: draft.role, location: draft.location, language: draft.language, source_url: draft.source_url, retrieved: draft.retrieved } }) }); const result = await response.json(); if (!response.ok) { setMessage(result.detail || "Could not start workflow."); return; } setThreadId(result.thread_id); setEvidence(result.evidence?.candidates || []); setStep(2); setMessage("Evidence is ready for review."); };
  const resumeWorkflow = async (action: "approve" | "reject") => { if (!threadId) return; const response = await fetch(`/api/workflow/${threadId}/resume`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ decision: { action, evidence_ids: action === "approve" ? [] : [], notes: "" } }) }); if (!response.ok) { setMessage("Could not save the review."); return; } setStep(action === "approve" ? 3 : 1); setMessage(action === "approve" ? "Evidence approved. Generation can continue." : "Evidence rejected. Review the job again."); };
  return <section className="form-page"><h1>Start an application</h1><p className="lede">Step {step} of 4 · Paste a job post, review evidence, then generate a targeted application.</p><ol aria-label="Application progress"><li aria-current={step === 1 ? "step" : undefined}>Job post</li><li aria-current={step === 2 ? "step" : undefined}>Evidence</li><li aria-current={step === 3 ? "step" : undefined}>Draft</li><li aria-current={step === 4 ? "step" : undefined}>Review</li></ol>
    <form className="create-record-form" onSubmit={(event) => { event.preventDefault(); setMessage(draft.text.trim() ? "Draft saved in this browser session." : "Paste the job description first."); }}>
      <label>Job post text<textarea rows={10} value={draft.text} onChange={(event) => update("text", event.target.value)} required /></label>
      <label>Public job URL<input type="url" value={draft.source_url} onChange={(event) => update("source_url", event.target.value)} placeholder="https://…" /></label>
      <button className="button button-secondary" type="button" onClick={() => void fetchUrl()} disabled={!draft.source_url}>Fetch URL</button>
      <div className="editor-field-grid"><label>Company<input value={draft.company} onChange={(event) => update("company", event.target.value)} required /></label><label>Role<input value={draft.role} onChange={(event) => update("role", event.target.value)} required /></label><label>Location<input value={draft.location} onChange={(event) => update("location", event.target.value)} /></label><label>Language<input value={draft.language} onChange={(event) => update("language", event.target.value)} /></label></div>
      <button className="button button-primary" type="button" onClick={() => void startWorkflow()} disabled={!draft.text.trim() || !draft.company || !draft.role}>Build application</button>{step === 2 && <div className="review-card"><h2>Review evidence</h2>{evidence.length ? <ul>{evidence.map((item, index) => <li key={`${item.source_path}-${index}`}><strong>{item.requirement_id}</strong> · {item.excerpt}<small>Source: {item.source_path} · Confidence: {Math.round(item.confidence * 100)}%</small></li>)}</ul> : <p>No matching profile evidence was found. You can reject this set and revise the job details.</p>}<button className="button button-primary" type="button" onClick={() => void resumeWorkflow("approve")}>Approve evidence</button><button className="button button-secondary" type="button" onClick={() => void resumeWorkflow("reject")}>Reject and revise</button></div>}{step === 3 && <p role="status">Generation complete. Final review is ready.</p>}{message && <p role="status">{message}</p>}
    </form>
  </section>;
}
