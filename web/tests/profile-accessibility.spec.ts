import { expect, test } from "@playwright/test";

const fixture = {
  slug: "accessibility-fixture",
  company: "Example Company",
  role: "Example role",
  employment_type: "Full-time",
  location: "Remote",
  start: "2024-01",
  end: "present",
  body: "A safe fixture for the browser test.",
};

function luminance(rgb: string) {
  const channels = rgb.match(/\d+(?:\.\d+)?/g)?.slice(0, 3).map(Number) || [];
  return channels.map((value) => {
    const channel = value / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  }).reduce((total, value, index) => total + value * [0.2126, 0.7152, 0.0722][index], 0);
}

test("profile edit flow has accessible labels, focus, contrast, and errors", async ({ page }) => {
  await page.addInitScript((record) => {
    const originalFetch = window.fetch;
    window.fetch = (input, init) => {
      const path = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url, window.location.href).pathname;
      if (path === "/api/records/experience/accessibility-fixture") return Promise.resolve(new Response(JSON.stringify(record), { headers: { "Content-Type": "application/json" } }));
      if (path === "/api/proposals" && init?.method === "POST") return Promise.resolve(new Response(JSON.stringify({ detail: "Unavailable" }), { status: 500, headers: { "Content-Type": "application/json" } }));
      return originalFetch(input, init);
    };
  }, fixture);
  await page.goto("/profile/experience/accessibility-fixture");

  const company = page.getByLabel("Company");
  await expect(company).toHaveAttribute("name", "company");
  await company.focus();
  await expect(company).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Role")).toBeFocused();

  const ratio = await page.getByRole("button", { name: "Review changes" }).evaluate((button) => {
    const style = getComputedStyle(button);
    return [style.color, style.backgroundColor];
  });
  const contrast = (Math.max(luminance(ratio[0]), luminance(ratio[1])) + 0.05) / (Math.min(luminance(ratio[0]), luminance(ratio[1])) + 0.05);
  expect(contrast).toBeGreaterThanOrEqual(4.5);

  await company.fill("Accessible Company");
  await page.getByRole("button", { name: "Review changes" }).click();
  await expect(page.locator("p[role='alert']")).toHaveText("Could not create a proposal. Check your connection and try again.");
});
