"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Star } from "lucide-react";
import MypageShell from "@/components/mypage-shell";
import FavoriteStarButton from "@/components/favorite-star-button";
import { useAuth } from "@/components/auth-provider";
import { useFavorites } from "@/components/favorites-provider";
import { fetchFavorites, type FavoriteCardItem } from "@/lib/favorites";
import { restaurantDetailPath } from "@/lib/gourmet";

export default function MypageFavoritesPage() {
  const { user } = useAuth();
  const { favoritedIds } = useFavorites();
  const [items, setItems] = useState<FavoriteCardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.username) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await fetchFavorites(user.id);
        if (!cancelled) setItems(list);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "오류");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.username]);

  useEffect(() => {
    setItems((prev) => prev.filter((i) => favoritedIds.has(i.store_id)));
  }, [favoritedIds]);

  return (
    <MypageShell title="즐겨찾기">
      {loading ? (
        <p className="text-sm text-[#6e6e73]">불러오는 중…</p>
      ) : error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-black/15 bg-white p-10 text-center">
          <Star className="mx-auto h-10 w-10 text-amber-400/80" />
          <p className="mt-4 text-sm text-[#6e6e73]">
            아직 즐겨찾기한 매장이 없습니다.
            <br />
            맛집 카드의 별 아이콘을 눌러 추가해 보세요.
          </p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-full bg-[#1d1d1f] px-5 py-2 text-sm text-white"
          >
            맛집 둘러보기
          </Link>
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {items.map((item) => (
            <li
              key={item.restaurant_id}
              className="overflow-hidden rounded-2xl border border-black/10 bg-white shadow-sm"
            >
              <div className="relative aspect-[16/10] bg-[#f5f5f7]">
                <Link href={restaurantDetailPath(item.store_id)} className="block h-full">
                  <Image
                    src={item.image_url || "/placeholder.svg"}
                    alt={item.name}
                    fill
                    className="object-cover"
                    sizes="(max-width: 640px) 100vw, 320px"
                  />
                </Link>
                <div className="absolute right-2 top-2">
                  <FavoriteStarButton storeId={item.store_id} />
                </div>
              </div>
              <div className="p-4">
                <Link
                  href={restaurantDetailPath(item.store_id)}
                  className="font-semibold text-[#1d1d1f] hover:underline"
                >
                  {item.name}
                </Link>
                {item.category_label ? (
                  <p className="mt-1 text-xs text-[#6e6e73]">{item.category_label}</p>
                ) : null}
                {item.district ? (
                  <p className="mt-0.5 text-xs text-[#86868b]">{item.district}</p>
                ) : null}
                {item.signature_menu ? (
                  <p className="mt-2 line-clamp-2 text-sm text-[#6e6e73]">
                    {item.signature_menu}
                  </p>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
    </MypageShell>
  );
}
