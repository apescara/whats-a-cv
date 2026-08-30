const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  const response = await fetch(`${agentUrl}/applications`, { cache: "no-store" });
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}
