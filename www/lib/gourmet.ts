/** GourmetMate API */

import type { UserCoords } from "@/lib/gourmet-location";
import { appendLocationParams } from "@/lib/gourmet-location";

export type MenuItem = {
  name: string;
  price: number;
  note: string;
};

export type RestaurantDetail = {
  id: number;
  name: string;
  category_slug: string;
  category_label: string;
  district: string;
  description: string;
  image_url: string;
  closed_weekdays: number[];
  closed_weekdays_label: string;
  address: string;
  opening_hours: string;
  phone: string | null;
  instagram_url: string | null;
  reservation_available: boolean;
  reservation_note: string;
  menu_items: MenuItem[];
  latitude: number | null;
  longitude: number | null;
};

export async function fetchRestaurantDetail(
  restaurantId: number
): Promise<RestaurantDetail | null> {
  const res = await fetch(`/api/gourmet/restaurants/${restaurantId}`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  return (await res.json()) as RestaurantDetail;
}

export function restaurantDetailPath(id: number): string {
  return `/restaurants/${id}`;
}

export function formatPrice(won: number): string {
  return `${won.toLocaleString("ko-KR")}원`;
}

export type RestaurantSearchItem = {
  id: number;
  name: string;
  image_url: string;
  district?: string;
  distance_km?: number | null;
  category_slug?: string | null;
  category_label?: string | null;
  rank?: number | null;
};

export type RestaurantSearchResult = {
  query: string;
  summary: string;
  matched_topics: { slug: string; title: string; emoji: string }[];
  restaurants: RestaurantSearchItem[];
  nearby_mode?: boolean;
  pagination?: {
    offset: number;
    limit: number;
    total: number;
    has_more: boolean;
  };
};

export async function fetchRestaurantSearch(
  query: string,
  coords?: UserCoords | null,
  pagination?: { offset?: number; limit?: number },
): Promise<RestaurantSearchResult> {
  const params = new URLSearchParams({ q: query.trim() });
  appendLocationParams(params, coords ?? null);
  const off = pagination?.offset;
  const lim = pagination?.limit;
  if (typeof off === "number") params.set("offset", String(off));
  if (typeof lim === "number") params.set("limit", String(lim));
  const res = await fetch(`/api/gourmet/search?${params}`, { cache: "no-store" });
  if (!res.ok) throw new Error("search failed");
  return (await res.json()) as RestaurantSearchResult;
}
