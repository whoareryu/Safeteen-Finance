import { proxyToBackend } from "@/lib/backend-proxy";
import { fetchStandaloneWeather } from "@/lib/standalone-weather";
import { useStandaloneApi } from "@/lib/standalone-gourmet-api";

export async function GET(request: Request) {
  if (useStandaloneApi()) {
    return fetchStandaloneWeather(request);
  }
  return proxyToBackend(request, "/api/weather");
}
