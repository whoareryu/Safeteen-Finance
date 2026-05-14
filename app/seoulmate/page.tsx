"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, MapPin } from "lucide-react";
import {
  SeoulHanokIcon,
  SeoulNamsanIcon,
  SeoulPalaceIcon,
  SeoulRiverIcon,
} from "@/components/seoulmate/seoul-symbol-svgs";

type CategoryId = "nature" | "history" | "attraction" | "restaurant";

const CATEGORIES: {
  id: CategoryId;
  label: string;
  labelKo: string;
  detailNote: string;
  placeholderPlaces: { name: string; area: string }[];
}[] = [
  {
    id: "nature",
    label: "Nature",
    labelKo: "자연",
    detailNote: "산·공원·산책로 추천 (예정)",
    placeholderPlaces: [
      { name: "북한산국립공원", area: "도봉구 일대" },
      { name: "남산공원", area: "중구" },
      { name: "한강공원 산책로", area: "여러 자치구" },
    ],
  },
  {
    id: "history",
    label: "History",
    labelKo: "역사",
    detailNote: "궁·유적·한양도성 추천 (예정)",
    placeholderPlaces: [
      { name: "경복궁 · 광화문", area: "종로구" },
      { name: "덕수궁 돌담길", area: "중구" },
      { name: "서울한양도성", area: "성북·종로" },
    ],
  },
  {
    id: "attraction",
    label: "Activities",
    labelKo: "놀이·체험",
    detailNote: "놀이공원·테마파크·체험형 액티비티 추천 (예정)",
    placeholderPlaces: [
      { name: "롯데월드 어드벤처", area: "송파구 잠실" },
      { name: "서울어린이대공원", area: "광진구 (동물원·놀이시설)" },
      { name: "코엑스 아쿠아리움", area: "강남구 (체험·관람)" },
    ],
  },
  {
    id: "restaurant",
    label: "Restaurant",
    labelKo: "맛집",
    detailNote: "식당·시장·카페거리 추천 (예정)",
    placeholderPlaces: [
      { name: "광장시장 먹거리", area: "종로구" },
      { name: "을지로·충무로 골목", area: "중구" },
      { name: "성수·연남 카페거리", area: "성동·마포" },
    ],
  },
];

export default function SeoulMatePage() {
  const [openId, setOpenId] = useState<CategoryId | null>(null);

  const toggle = (id: CategoryId) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  const open = CATEGORIES.find((c) => c.id === openId);

  return (
    <main className="min-h-screen bg-transparent px-6 pb-16 pt-24">
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-10">
        <div className="flex w-full flex-col items-center gap-4">
          <div className="flex flex-wrap items-end justify-center gap-3 md:gap-5">
            <SeoulHanokIcon className="h-10 w-14 md:h-12 md:w-16" />
            <SeoulNamsanIcon className="h-14 w-10 md:h-16 md:w-12" />
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 md:gap-4">
            <SeoulPalaceIcon className="h-9 w-12 md:h-11 md:w-14" />
            <h1 className="bg-gradient-to-r from-rose-400 via-amber-400 to-emerald-500 bg-clip-text px-2 text-center text-4xl font-bold tracking-tight text-transparent dark:from-rose-400 dark:via-amber-400 dark:to-emerald-500 md:text-6xl">
              SeoulMate
            </h1>
            <SeoulRiverIcon className="h-8 w-14 md:h-10 md:w-16" />
          </div>

          <p className="max-w-md text-center text-sm text-muted-foreground md:text-base">
            SeoulMate — 서울의 자연·역사·
            <span className="font-medium text-foreground/90">놀이·체험</span>·맛집을
            한곳에서 골라볼 수 있게 준비 중입니다. 항목을 누르면 추천 장소 목록이
            펼쳐집니다.
          </p>
        </div>

        <div className="w-full space-y-3">
          {CATEGORIES.map((cat) => {
            const isOpen = openId === cat.id;
            return (
              <div
                key={cat.id}
                className="overflow-hidden rounded-xl border border-border bg-card shadow-sm"
              >
                <button
                  type="button"
                  onClick={() => toggle(cat.id)}
                  className="flex w-full items-center justify-between gap-3 px-4 py-4 text-left transition hover:bg-muted/50"
                  aria-expanded={isOpen}
                >
                  <span className="flex flex-col gap-0.5">
                    <span className="text-lg font-semibold capitalize text-foreground">
                      {cat.label}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {cat.labelKo} · {cat.detailNote}
                    </span>
                  </span>
                  {isOpen ? (
                    <ChevronUp className="h-5 w-5 shrink-0 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-5 w-5 shrink-0 text-muted-foreground" />
                  )}
                </button>

                {isOpen && (
                  <div className="border-t border-border bg-muted/20 px-4 py-4">
                    <p className="mb-3 text-xs text-muted-foreground">
                      아래는 UI 구조용 예시입니다. 이후 실제 추천 데이터로
                      교체됩니다.
                    </p>
                    <ul className="space-y-3">
                      {cat.placeholderPlaces.map((p) => (
                        <li
                          key={p.name}
                          className="flex items-start gap-2 rounded-lg border border-border/60 bg-background/80 px-3 py-2.5"
                        >
                          <MapPin
                            className="mt-0.5 h-4 w-4 shrink-0 text-primary"
                            aria-hidden
                          />
                          <div>
                            <p className="font-medium text-foreground">{p.name}</p>
                            <p className="text-xs text-muted-foreground">{p.area}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {open && (
          <p className="text-center text-xs text-muted-foreground">
            선택됨: <strong className="text-foreground">{open.label}</strong> — 곧
            서울 기준 맞춤 추천으로 갱신됩니다.
          </p>
        )}
      </div>
    </main>
  );
}
