const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function GET(_request: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const response = await fetch(`${agentUrl}/applications/${encodeURIComponent(slug)}`, { cache: "no-store" });
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}

export async function DELETE(_request: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const response = await fetch(`${agentUrl}/applications/${encodeURIComponent(slug)}`, { method: "DELETE" });
  return new Response(response.body, { status: response.status, headers: { "content-type": response.headers.get("content-type") ?? "application/json" } });
}
