import { fetchStandaloneWeather } from "@/lib/standalone-weather";

export async function GET(request: Request) {
  return fetchStandaloneWeather(request);
}
