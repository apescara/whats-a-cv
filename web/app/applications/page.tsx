"use client";

import { useEffect, useState } from "react";

type Application = { slug: string; company: string; role: string; date: string; status: string; has_pdf: boolean; has_todo: boolean };

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { fetch("/api/applications").then((response) => response.ok ? response.json() : Promise.reject(new Error("Could not load applications."))).then(setApplications).catch((reason: Error) => setError(reason.message)); }, []);
  return <section>
    <p className="eyebrow">Workspace</p><h1>Applications</h1>
    <p className="lede">Review each tailored application, its source job post, CV, PDF, and preparation notes.</p>
    <a className="button button-primary" href="/create-cv">New application</a>
    {error && <p role="alert">{error}</p>}
    {!applications && !error && <p role="status">Loading applications…</p>}
    {applications?.length === 0 && <p className="empty-state">No applications yet.</p>}
    {applications && applications.length > 0 && <ul className="application-list">{applications.map((application) => <li className="application-card" key={application.slug}>
      <div><p className="eyebrow">{application.date || "Undated"}</p><h2><a href={`/applications/${application.slug}`}>{application.role}</a></h2><p>{application.company}</p></div>
      <div className="application-card-meta"><span>{application.status || "Draft"}</span>{application.has_pdf && <span>PDF ready</span>}{application.has_todo && <span>TODOs</span>}</div>
    </li>)}</ul>}
  </section>;
}
