"use client";

import { useEffect, useState } from "react";
import type { components } from "../../../../lib/api.generated";
import RecordEditor, { ContactEditor } from "./editor";

type RecordKind = components["schemas"]["RecordKind"];
type RecordData = { slug: string; body?: string; relative_path?: string; related_expertise?: { slug: string; name: string }[]; [key: string]: unknown };
const recordKinds: RecordKind[] = ["contact", "experience", "education", "certifications", "projects", "expertise", "languages"];

export default function RecordDetailPage({ params }: { params: Promise<{ kind: string; slug: string }> }) {
  const [record, setRecord] = useState<RecordData | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;
    params.then(({ kind, slug }) => {
      if (!recordKinds.includes(kind as RecordKind)) {
        setState("error");
        return;
      }
      return fetch(`/api/records/${kind as RecordKind}/${slug}`)
        .then((response) => {
          if (!response.ok) throw new Error("Record not found");
          return response.json() as Promise<RecordData>;
        })
        .then((data) => active && (setRecord(data), setState("ready")));
    }).catch(() => active && setState("error"));
    return () => { active = false; };
  }, [params]);

  if (state === "loading") return <p role="status">Loading record…</p>;
  if (state === "error" || !record) return <p role="alert">Record not found.</p>;

  const fields = Object.entries(record).filter(([key, value]) => value !== "" && !["slug", "body", "relative_path", "related_expertise", ...(record.type ? ["value"] : [])].includes(key));
  return (
    <article>
      <a href="/profile">← Profile</a>
      <h1>{String(record.role || record.name || record.qualification || record.language || record.type || record.slug)}</h1>
      <p className="source-path">Source: {String(record.relative_path || "repository record")}</p>
      <section className="record-summary" aria-labelledby="record-details-title">
        <h2 id="record-details-title">Record details</h2>
        <dl className="record-fields">
          {fields.map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{typeof value === "string" ? value : JSON.stringify(value)}</dd></div>)}
        </dl>
      </section>
      {Array.isArray(record.evidence) && <section aria-labelledby="evidence-title"><h2 id="evidence-title">Evidence</h2><ul>{record.evidence.map((item, index) => { const evidence = item as { text?: string; source?: { relative_path?: string } }; const match = evidence.source?.relative_path?.match(/^(contact|experience|education|certifications|projects|expertise|languages)\/([^/]+)\.md$/); return <li key={index}>{match ? <a href={`/profile/${match[1]}/${match[2]}`}>{evidence.text}</a> : evidence.text}</li>; })}</ul></section>}
      {record.related_expertise?.length ? <section aria-labelledby="linked-skills-title"><h2 id="linked-skills-title">Linked skills</h2><ul>{record.related_expertise.map((skill) => <li key={skill.slug}><a href={`/profile/expertise/${skill.slug}`}>{skill.name}</a></li>)}</ul></section> : null}
      {record.body && <pre className="markdown-preview">{String(record.body)}</pre>}
      {record.type ? <ContactEditor record={record} /> : record.role && record.company ? <RecordEditor record={record} kind="experience" /> : record.qualification ? <RecordEditor record={record} kind="education" /> : record.issuer ? <RecordEditor record={record} kind="certifications" /> : record.category ? <RecordEditor record={record} kind="expertise" /> : record.language ? <RecordEditor record={record} kind="languages" /> : record.name ? <RecordEditor record={record} kind="projects" /> : null}
    </article>
  );
}
