"use client";

import { useEffect, useState } from "react";
import type { components } from "../../lib/api.generated";

type RecordKind = components["schemas"]["RecordKind"];
type RecordSummary = { slug: string };

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
  const [counts, setCounts] = useState<Partial<Record<RecordKind, number>>>({});
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all(
      recordKinds.map(async ({ kind }) => {
        const response = await fetch(`/api/records/${kind}`);
        if (!response.ok) throw new Error(`Could not load ${kind}`);
        return [kind, (await response.json() as RecordSummary[]).length] as const;
      }),
    )
      .then((entries) => active && setCounts(Object.fromEntries(entries)))
      .catch(() => active && setError(true));

    return () => { active = false; };
  }, []);

  return (
    <section>
      <h1>Profile</h1>
      <p>Manage the evidence behind your applications.</p>
      {error && <p role="alert">Record counts are unavailable.</p>}
      <nav className="record-tabs" aria-label="Profile record types">
        {recordKinds.map(({ kind, label }) => (
          <a className="record-tab" href={`/profile?kind=${kind}`} key={kind}>
            <span>{label}</span>
            <span aria-label={`${counts[kind] ?? "Loading"} records`}>
              {counts[kind] ?? "…"}
            </span>
          </a>
        ))}
      </nav>
    </section>
  );
}
