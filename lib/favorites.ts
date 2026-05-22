export type FavoriteCardItem = {
  store_id: number;
  restaurant_id: number;
  name: string;
  image_url: string;
  district: string;
  category_slug: string | null;
  category_label: string | null;
  signature_menu: string;
};

function favoriteHeaders(userId: number): HeadersInit {
  return { "X-User-Id": String(userId) };
}

export async function fetchFavoriteStoreIds(userId: number): Promise<number[]> {
  const res = await fetch(`/api/gourmet/favorites/store-ids`, {
    headers: favoriteHeaders(userId),
  });
  if (!res.ok) return [];
  const data = (await res.json()) as { favorited_store_ids: number[] };
  return data.favorited_store_ids ?? [];
}

export async function fetchFavorites(userId: number): Promise<FavoriteCardItem[]> {
  const res = await fetch(`/api/gourmet/favorites`, {
    headers: favoriteHeaders(userId),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string" ? body.detail : "즐겨찾기를 불러오지 못했습니다."
    );
  }
  return (await res.json()) as FavoriteCardItem[];
}

export async function toggleFavorite(
  userId: number,
  storeId: number
): Promise<{ favorited: boolean; message: string }> {
  const res = await fetch(`/api/gourmet/favorites/toggle`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...favoriteHeaders(userId),
    },
    body: JSON.stringify({ store_id: storeId }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string" ? body.detail : "즐겨찾기 처리에 실패했습니다."
    );
  }
  const data = (await res.json()) as {
    favorited: boolean;
    message: string;
  };
  return { favorited: data.favorited, message: data.message };
}
