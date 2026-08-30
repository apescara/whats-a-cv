"use client";

import { useEffect, useState } from "react";
import type { components } from "../../lib/api.generated";

type RecordKind = components["schemas"]["RecordKind"];
type RecordSummary = {
  slug: string;
  title: string;
  valid: boolean;
  relative_path: string;
  error?: string | null;
};

const recordKinds: { kind: RecordKind; label: string }[] = [
  { kind: "experience", label: "Experience" },
  { kind: "education", label: "Education" },
  { kind: "certifications", label: "Certifications" },
  { kind: "projects", label: "Projects" },
  { kind: "expertise", label: "Expertise" },
  { kind: "languages", label: "Languages" },
  { kind: "contact", label: "Contact" },
];

export default function ProfilePage() {
  const [kind, setKind] = useState<RecordKind>("experience");
  const [counts, setCounts] = useState<Partial<Record<RecordKind, number>>>({});
  const [records, setRecords] = useState<RecordSummary[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;
    setState("loading");
    fetch(`/api/records/${kind}`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load records");
        return response.json() as Promise<RecordSummary[]>;
      })
      .then((nextRecords) => {
        if (!active) return;
        setRecords(nextRecords);
        setCounts((current) => ({ ...current, [kind]: nextRecords.length }));
        setState("ready");
      })
      .catch(() => active && setState("error"));

    return () => { active = false; };
  }, [kind]);

  return (
    <section>
      <h1>Profile</h1>
      <p>Manage the evidence behind your applications.</p>
      {state === "error" && <p role="alert">Records are unavailable.</p>}
      <nav className="record-tabs" aria-label="Profile record types">
        {recordKinds.map(({ kind, label }) => (
          <a className="record-tab" href={`/profile?kind=${kind}`} onClick={() => setKind(kind)} key={kind}>
            <span>{label}</span>
            <span aria-label={`${counts[kind] ?? "Loading"} records`}>
              {counts[kind] ?? "…"}
            </span>
          </a>
        ))}
      </nav>
      <section aria-labelledby="record-list-title">
        <h2 id="record-list-title">{recordKinds.find((item) => item.kind === kind)?.label}</h2>
        {state === "loading" && <p role="status">Loading records…</p>}
        {state === "ready" && records.length === 0 && <p>No records yet.</p>}
        {state === "ready" && records.length > 0 && (
          <ul className="record-list">
            {records.map((record) => (
              <li className="record-card" key={record.slug}>
                <a href={`/profile/${kind}/${record.slug}`}><strong>{record.title}</strong></a>
                <span>{record.slug}</span>
                <span className={`validation-state ${record.valid ? "strong" : "gap"}`}>
                  {record.valid ? "Strong" : "Gap"}
                </span>
                <small>{record.relative_path}</small>
              </li>
            ))}
          </ul>
        )}
      </section>
      <p><a href="/profile/preferences">Edit search preferences</a> <small>(not CV evidence)</small></p>
    </section>
  );
}
