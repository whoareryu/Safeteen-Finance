import { standaloneWeatherIcon } from "@/lib/standalone-weather";

export async function GET(request: Request) {
  const code = new URL(request.url).searchParams.get("code") ?? "";
  return standaloneWeatherIcon(code);
}
