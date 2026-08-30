const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function GET(_request: Request, { params }: { params: Promise<{ slug: string; file: string }> }) {
  const { slug, file } = await params;
  const response = await fetch(`${agentUrl}/applications/${encodeURIComponent(slug)}/${encodeURIComponent(file)}`, { cache: "no-store" });
  return new Response(response.body, { status: response.status, headers: { "content-type": response.headers.get("content-type") ?? "text/plain; charset=utf-8", "content-disposition": response.headers.get("content-disposition") ?? "inline" } });
}
