export type TopicRestaurant = {
  id: number;
  name: string;
  genre: string;
  road_address: string;
  latitude: number | null;
  longitude: number | null;
};

export type TopicRow = {
  slug: string;
  title: string;
  subtitle: string;
  emoji: string;
  restaurants: TopicRestaurant[];
};

export async function fetchTopicFeed(
  lat: number | null,
  lng: number | null,
  n = 5,
): Promise<TopicRow[]> {
  const params = new URLSearchParams({ n: String(n) });
  if (lat != null) params.set("lat", String(lat));
  if (lng != null) params.set("lng", String(lng));
  const res = await fetch(`/api/gourmet/topics/feed?${params}`, { cache: "no-store" });
  if (!res.ok) return [];
  return (await res.json()) as TopicRow[];
}
