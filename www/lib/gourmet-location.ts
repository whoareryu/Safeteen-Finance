/** Gourmet API — 사용자 위치 쿼리 파라미터 */

export type UserCoords = {
  lat: number;
  lng: number;
};

export function appendLocationParams(
  params: URLSearchParams,
  coords: UserCoords | null | undefined
): void {
  if (!coords) return;
  params.set("lat", String(coords.lat));
  params.set("lng", String(coords.lng));
}

export function formatDistanceKm(km: number | undefined | null): string | null {
  if (km == null || Number.isNaN(km)) return null;
  if (km < 1) return `${Math.round(km * 1000)}m`;
  return `${km.toFixed(1)}km`;
}
