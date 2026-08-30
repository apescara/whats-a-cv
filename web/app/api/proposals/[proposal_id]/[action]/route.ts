import { NextRequest } from "next/server";

const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function POST(_request: NextRequest, { params }: { params: Promise<{ proposal_id: string; action: string }> }) {
  const { proposal_id, action } = await params;
  if (action !== "approve" && action !== "reject") return new Response("Not found", { status: 404 });
  const response = await fetch(`${agentUrl}/proposals/${encodeURIComponent(proposal_id)}/${action}`, { method: "POST" });
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}
