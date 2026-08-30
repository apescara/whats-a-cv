const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";
export async function GET(_: Request, { params }: { params: Promise<{ threadId: string }> }) {
  const { threadId } = await params;
  const response = await fetch(`${agentUrl}/workflow/${encodeURIComponent(threadId)}/events`);
  return new Response(response.body, { status: response.status, headers: { "content-type": "text/event-stream" } });
}
