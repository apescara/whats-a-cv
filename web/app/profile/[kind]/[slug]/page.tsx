"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import type { components } from "../../../../lib/api.generated";
import MarkdownPreview from "../../../markdown-preview";
import RecordEditor, { ContactEditor } from "./editor";

type RecordKind = components["schemas"]["RecordKind"];
type RecordData = { slug: string; body?: string; relative_path?: string; related_expertise?: { slug: string; name: string }[]; related_experience?: { slug: string; role: string; company: string }[]; [key: string]: unknown };
const recordKinds: RecordKind[] = ["contact", "experience", "education", "certifications", "projects", "expertise", "languages"];

export default function RecordDetailPage({ params }: { params: Promise<{ kind: string; slug: string }> }) {
  const [record, setRecord] = useState<RecordData | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [editing, setEditing] = useState(false);

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

  const fields = Object.entries(record).filter(([key, value]) => value !== "" && !["slug", "body", "relative_path", "evidence", "related_expertise", "related_experience", ...(record.type ? ["value"] : [])].includes(key));
  const modalEditor = record.role && record.company ? "experience" : record.category ? "expertise" : null;
  return (
    <article>
      <a href="/profile">← Profile</a>
      <div className="record-heading"><div><h1>{String(record.role || record.name || record.qualification || record.language || record.type || record.slug)}</h1><p className="source-path">Source: {String(record.relative_path || "repository record")}</p></div>{modalEditor && <button className="button button-secondary" type="button" onClick={() => setEditing(true)}>Edit {modalEditor}</button>}</div>
      <section className="record-summary" aria-labelledby="record-details-title">
        <h2 id="record-details-title">Record details</h2>
        <dl className="record-fields">
          {fields.map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{typeof value === "string" ? value : JSON.stringify(value)}</dd></div>)}
        </dl>
      </section>
      {Array.isArray(record.evidence) && record.evidence.length > 0 && <section aria-labelledby="evidence-title"><h2 id="evidence-title">Evidence</h2><ul>{record.evidence.map((item, index) => { const evidence = item as { text?: string; source?: { relative_path?: string } }; const match = evidence.source?.relative_path?.match(/^(contact|experience|education|certifications|projects|expertise|languages)\/([^/]+)\.md$/); return <li key={index}>{match ? <a href={`/profile/${match[1]}/${match[2]}`}>{evidence.text}</a> : evidence.text}</li>; })}</ul></section>}
      {record.related_expertise?.length ? <section className="related-records" aria-labelledby="linked-skills-title"><h2 id="linked-skills-title">Expertise used here</h2><div className="expertise-links">{record.related_expertise.map((skill) => <a className="expertise-link" href={`/profile/expertise/${skill.slug}`} key={skill.slug}>{skill.name}</a>)}</div></section> : null}
      {record.related_experience?.length ? <section className="related-records" aria-labelledby="linked-experience-title"><h2 id="linked-experience-title">Used in experience</h2><div className="experience-links">{record.related_experience.map((experience) => <a className="experience-link" href={`/profile/experience/${experience.slug}`} key={experience.slug}><strong>{experience.role}</strong><span>{experience.company}</span></a>)}</div></section> : null}
      {record.body && <section className="record-narrative" aria-labelledby="record-narrative-title"><h2 id="record-narrative-title">Details</h2><MarkdownPreview content={String(record.body)} /></section>}
      {modalEditor ? editing && <EditorDialog onClose={() => setEditing(false)}><RecordEditor record={record} kind={modalEditor} /></EditorDialog> : record.type ? <ContactEditor record={record} /> : record.qualification ? <RecordEditor record={record} kind="education" /> : record.issuer ? <RecordEditor record={record} kind="certifications" /> : record.language ? <RecordEditor record={record} kind="languages" /> : record.name ? <RecordEditor record={record} kind="projects" /> : null}
    </article>
  );
}

function EditorDialog({ children, onClose }: { children: ReactNode; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { dialog.current?.showModal(); return () => dialog.current?.close(); }, []);
  return <dialog className="editor-dialog" ref={dialog} aria-labelledby="editor-dialog-title" onClose={onClose}><div className="editor-dialog-heading"><div><h2 id="editor-dialog-title">Edit record</h2><p>Review your changes before they are saved.</p></div><button className="button button-secondary" type="button" onClick={() => dialog.current?.close()}>Close</button></div>{children}</dialog>;
}
