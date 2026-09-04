import { expect, test } from "@playwright/test";

const bundle = { slug: "markdown-fixture", path: "applications/markdown-fixture", metadata: { company: "Example", role: "Example role", location: "Remote", date: "2026-09-03", language: "English", source_url: "", retrieved: "", status: "Draft", artifacts: { next_steps: "next-steps.mdx" } }, files: ["job-post.md", "next-steps.mdx"], extra_files: [], warnings: [] };

test("read-only Markdown artifacts render as a safe preview", async ({ page }) => {
  await page.addInitScript((application) => { const originalFetch = window.fetch; window.fetch = (input, init) => { const path = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url, window.location.href).pathname; if (path === "/api/applications/markdown-fixture") return Promise.resolve(new Response(JSON.stringify(application), { headers: { "Content-Type": "application/json" } })); if (path.endsWith("/job-post.md")) return Promise.resolve(new Response("---\ncompany: Example\n---\n# Role\n\n## Responsibilities\n\n- Build **reliable** systems\n- Review `code`", { headers: { "Content-Type": "text/plain" } })); if (path.endsWith("/next-steps.mdx")) return Promise.resolve(new Response("# Next steps\n\n| Requirement | Evidence |\n| --- | --- |\n| Python | Strong |", { headers: { "Content-Type": "text/plain" } })); return originalFetch(input, init); }; }, bundle);
  await page.goto("/applications/markdown-fixture");
  await page.getByRole("button", { name: "Job post" }).click();
  await expect(page.getByRole("heading", { name: "Role", exact: true })).toBeVisible();
  await expect(page.locator(".markdown-content li")).toHaveText(["Build reliable systems", "Review code"]);
  await expect(page.getByText("company: Example")).toHaveCount(0);
  await page.getByRole("button", { name: "Next steps" }).click();
  await expect(page.getByRole("columnheader", { name: "Requirement" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Python" })).toBeVisible();
});
