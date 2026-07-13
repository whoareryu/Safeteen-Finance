import { proxyToBackend } from "@/lib/backend-proxy";
import { standaloneWeatherIcon } from "@/lib/standalone-weather";
import { useStandaloneApi } from "@/lib/standalone-gourmet-api";

export async function GET(request: Request) {
  if (useStandaloneApi()) {
    const code = new URL(request.url).searchParams.get("code") ?? "";
    return standaloneWeatherIcon(code);
  }
  return proxyToBackend(request, "/api/weather/icon");
}
