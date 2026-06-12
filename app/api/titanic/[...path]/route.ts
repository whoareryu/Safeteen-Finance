import { proxyToBackend } from "@/lib/backend-proxy";

type RouteContext = { params: Promise<{ path: string[] }> };

async function handle(request: Request, context: RouteContext) {
  const { path } = await context.params;
  const segment = (path ?? []).join("/");
  return proxyToBackend(request, `/api/titanic/${segment}`);
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;

