/** GourmetMate API — 매장 조회 수 */

export async function recordRestaurantView(restaurantId: number): Promise<number> {
  const res = await fetch(`/api/gourmet/restaurants/${restaurantId}/view`, {
    method: "POST",
  });
  if (!res.ok) return 0;
  const body = (await res.json()) as { view_count?: number };
  return body.view_count ?? 0;
}
