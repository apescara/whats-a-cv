import { NextRequest } from "next/server";

const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const response = await fetch(`${agentUrl}/proposals`, { method: "POST", headers: { "content-type": "application/json" }, body: await request.text() });
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}
