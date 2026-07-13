import { proxyToBackend } from "@/lib/backend-proxy";
import {
  handleStandaloneGourmetPath,
  useStandaloneApi,
} from "@/lib/standalone-gourmet-api";

type RouteContext = { params: Promise<{ path: string[] }> };

async function handle(request: Request, context: RouteContext) {
  const { path } = await context.params;
  const segment = (path ?? []).join("/");
  if (useStandaloneApi()) {
    return handleStandaloneGourmetPath(request, segment);
  }
  return proxyToBackend(request, `/api/gourmet/${segment}`);
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
