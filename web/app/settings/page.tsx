"use client";

import { FormEvent, useEffect, useState } from "react";

const steps = [
  ["default", "Default model", "Used unless a step has its own model."],
  ["requirements", "Requirements", "Extracts job requirements."],
  ["evidence", "Evidence", "Ranks the evidence for review."],
  ["cv", "CV", "Drafts the tailored CV."],
  ["next_steps", "Next steps", "Drafts preparation notes."],
] as const;

type Settings = { keys: Record<string, boolean>; models: Record<string, string> };

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [models, setModels] = useState<Record<string, string>>({});
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/settings").then(async (response) => {
      if (!response.ok) throw new Error("Could not load settings.");
      const loaded: Settings = await response.json();
      setSettings(loaded);
      setModels(loaded.models);
    }).catch((error: Error) => setMessage(error.message));
  }, []);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    const api_keys = Object.fromEntries(Object.entries(keys).filter(([, value]) => value.trim()));
    const response = await fetch("/api/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_keys, models }),
    });
    const result = await response.json();
    if (!response.ok) return setMessage(result.detail || "Could not save settings.");
    setSettings(result);
    setModels(result.models);
    setKeys({});
    setMessage("Saved for this session. New applications will use these settings right away.");
  }

  return <section className="settings-page">
    <h1>Settings</h1>
    <p className="lede">Choose the AI provider and model for each part of your application workflow.</p>
    <p className="privacy-note">Values entered here override <code>.env</code> for this session and are never shown again. Restarting the agent returns to your <code>.env</code> defaults.</p>
    <form className="settings-form" onSubmit={save}>
      <fieldset>
        <legend>Provider API keys</legend>
        <p className="field-hint">Paste a key to add or replace it. Leave a field blank to keep the saved key.</p>
        {(["openai", "anthropic", "google"] as const).map((provider) => <label key={provider}>
          {provider === "openai" ? "OpenAI" : provider === "anthropic" ? "Anthropic" : "Google"} {settings?.keys[provider] ? "(configured)" : "(not configured)"}
          <input type="password" autoComplete="off" value={keys[provider] || ""} onChange={(event) => setKeys({ ...keys, [provider]: event.target.value })} placeholder="Paste a new API key" />
        </label>)}
      </fieldset>
      <fieldset>
        <legend>Models by workflow step</legend>
        <p className="field-hint">Use <code>provider:model</code>, such as <code>openai:gpt-5.6-luna</code>. Blank step fields use the default model.</p>
        {steps.map(([name, label, hint]) => <label key={name}>
          {label}
          <input required={name === "default"} value={models[name] || ""} onChange={(event) => setModels({ ...models, [name]: event.target.value })} placeholder={name === "default" ? "openai:gpt-5.6-luna" : "Use default model"} />
          <span className="field-hint">{hint}</span>
        </label>)}
      </fieldset>
      <button className="button button-primary" disabled={!settings}>Save settings</button>
      {message && <p className={message.startsWith("Saved") ? "settings-message success" : "settings-message"} role="status">{message}</p>}
    </form>
  </section>;
}
