"use client";

import { useState } from "react";

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState("");
  return <section>
    <a href="/profile">← Profile</a>
    <h1>Search preferences</h1>
    <p>These preferences guide opportunity evaluation and are not copied into CV evidence automatically.</p>
    <label className="record-editor">Notes<textarea rows={12} value={preferences} onChange={(event) => setPreferences(event.target.value)} placeholder="Target roles, locations, work mode, and priorities" /></label>
  </section>;
}
