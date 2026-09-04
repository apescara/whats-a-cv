const agentUrl = process.env.AGENT_INTERNAL_URL ?? "http://127.0.0.1:8000";

async function proxy(request: Request) {
  const response = await fetch(`${agentUrl}/settings`, {
    method: request.method,
    headers: request.method === "PUT" ? { "content-type": "application/json" } : undefined,
    body: request.method === "PUT" ? await request.text() : undefined,
  });
  return new Response(response.body, { status: response.status, headers: { "content-type": "application/json" } });
}

export const GET = proxy;
export const PUT = proxy;
