const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";
export async function POST(request: Request) { const response = await fetch(`${agentUrl}/job-url`, { method: "POST", headers: { "content-type": "application/json" }, body: await request.text() }); return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } }); }
