import { NextRequest } from "next/server";

const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function GET(_request: NextRequest, { params }: { params: Promise<{ proposal_id: string }> }) {
  const { proposal_id } = await params;
  const response = await fetch(`${agentUrl}/proposals/${encodeURIComponent(proposal_id)}`);
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}
