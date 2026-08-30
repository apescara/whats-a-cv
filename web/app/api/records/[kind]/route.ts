import { NextRequest } from "next/server";

const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ kind: string }> },
) {
  const { kind } = await params;
  const response = await fetch(`${agentUrl}/records/${encodeURIComponent(kind)}`);
  return new Response(response.body, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
  });
}
