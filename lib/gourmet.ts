/** GourmetMate API */

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
  view_count: number;
  closed_weekdays: number[];
  closed_weekdays_label: string;
  address: string;
  opening_hours: string;
  phone: string | null;
  instagram_url: string | null;
  reservation_available: boolean;
  reservation_note: string;
  menu_items: MenuItem[];
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

export async function recordRestaurantView(restaurantId: number): Promise<number> {
  const res = await fetch(`/api/gourmet/restaurants/${restaurantId}/view`, {
    method: "POST",
  });
  if (!res.ok) return 0;
  const body = (await res.json()) as { view_count?: number };
  return body.view_count ?? 0;
}

export function restaurantDetailPath(id: number): string {
  return `/restaurants/${id}`;
}

export function formatPrice(won: number): string {
  return `${won.toLocaleString("ko-KR")}원`;
}

export type RestaurantSearchItem = {
  rank: number;
  id: number;
  name: string;
  category_slug: string;
  category_label: string;
  district: string;
  description: string;
  image_url: string;
  view_count: number;
};

export type RestaurantSearchResult = {
  query: string;
  summary: string;
  matched_topics: { slug: string; title: string; emoji: string }[];
  restaurants: RestaurantSearchItem[];
};

export async function fetchRestaurantSearch(
  query: string
): Promise<RestaurantSearchResult> {
  const params = new URLSearchParams({ q: query.trim() });
  const res = await fetch(`/api/gourmet/search?${params}`, { cache: "no-store" });
  if (!res.ok) throw new Error("search failed");
  return (await res.json()) as RestaurantSearchResult;
}
