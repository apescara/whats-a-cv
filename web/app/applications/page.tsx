"use client";

import { useEffect, useState } from "react";

type Application = { slug: string; company: string; role: string; date: string; status: string; has_pdf: boolean; has_todo: boolean };

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[] | null>(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [deleting, setDeleting] = useState(false);
  useEffect(() => { fetch("/api/applications").then((response) => response.ok ? response.json() : Promise.reject(new Error("Could not load applications."))).then(setApplications).catch((reason: Error) => setError(reason.message)); }, []);
  const isDraft = (application: Application) => !application.status || ["draft", "drafting"].includes(application.status.toLowerCase());
  const drafts = applications?.filter(isDraft) ?? [];
  const completed = applications?.filter((application) => !isDraft(application)) ?? [];
  const removeDrafts = async () => {
    if (!selected.length || !window.confirm(`Delete ${selected.length} selected draft${selected.length === 1 ? "" : "s"}? This cannot be undone.`)) return;
    setDeleting(true); setError("");
    try {
      const results = await Promise.all(selected.map((slug) => fetch(`/api/applications/${encodeURIComponent(slug)}`, { method: "DELETE" })));
      if (results.some((response) => !response.ok)) setError("Some drafts could not be deleted. Refresh and try again.");
      else { setApplications((current) => current?.filter((application) => !selected.includes(application.slug)) ?? []); setSelected([]); }
    } catch { setError("Drafts could not be deleted. Check your connection and try again."); }
    finally { setDeleting(false); }
  };
  return <section>
    <h1>Applications</h1>
    <p className="lede">Review each tailored application, its source job post, CV, PDF, and preparation notes.</p>
    <a className="button button-primary" href="/create-cv">New application</a>
    {error && <p role="alert">{error}</p>}
    {!applications && !error && <p role="status">Loading applications…</p>}
    {applications?.length === 0 && <p className="empty-state">No applications yet.</p>}
    {completed.length > 0 && <section className="application-section" aria-labelledby="applications-title"><h2 id="applications-title">Your applications</h2><ul className="application-list">{completed.map((application) => <li className="application-card" key={application.slug}>
      <div><p className="eyebrow">{application.date || "Undated"}</p><h3><a href={`/applications/${application.slug}`}>{application.role}</a></h3><p>{application.company}</p></div>
      <div className="application-card-meta"><span>{application.status || "Draft"}</span>{application.has_pdf && <span>PDF ready</span>}{application.has_todo && <span>TODOs</span>}</div>
    </li>)}</ul></section>}
    {drafts.length > 0 && <section className="draft-section" aria-labelledby="drafts-title"><div className="section-heading"><div><h2 id="drafts-title">Drafts</h2><p>Review unfinished applications or remove the ones you no longer need.</p></div><button className="button button-danger" type="button" onClick={() => void removeDrafts()} disabled={!selected.length || deleting}>{deleting ? "Deleting…" : `Delete selected${selected.length ? ` (${selected.length})` : ""}`}</button></div><ul className="application-list">{drafts.map((application) => <li className="application-card selectable-application" key={application.slug}><label className="draft-checkbox"><input type="checkbox" checked={selected.includes(application.slug)} onChange={(event) => setSelected((current) => event.target.checked ? [...current, application.slug] : current.filter((slug) => slug !== application.slug))} /><span className="sr-only">Select {application.role} at {application.company}</span></label><div><p className="eyebrow">{application.date || "Undated"}</p><h3><a href={`/applications/${application.slug}`}>{application.role}</a></h3><p>{application.company}</p></div><div className="application-card-meta"><span>Draft</span>{application.has_pdf && <span>PDF ready</span>}{application.has_todo && <span>TODOs</span>}</div></li>)}</ul></section>}
  </section>;
}
