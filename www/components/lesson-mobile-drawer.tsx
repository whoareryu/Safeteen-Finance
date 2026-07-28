"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

type LessonItem = { href: string; label: string };
type LessonTopic = { id: string; label: string; items: LessonItem[] };

const TOPICS: LessonTopic[] = [
  {
    id: "titanic",
    label: "타이타닉",
    items: [
      { href: "/portfolio/titanic/data-collection", label: "1. 데이터 수집" },
      { href: "/portfolio/titanic/passenger-list", label: "2. 탑승자 목록" },
      { href: "/portfolio/titanic/smith-chat", label: "3. 스미스 선장과 대화" },
    ],
  },
  {
    id: "vision",
    label: "Vision",
    items: [
      { href: "/portfolio/vision/upload", label: "1. 이미지 업로드" },
      { href: "/portfolio/vision/object-detection", label: "2. 객체 탐지" },
    ],
  },
  {
    id: "plant",
    label: "식물 지식 수집",
    items: [{ href: "/portfolio/plant/crawler", label: "크롤러/스크래퍼" }],
  },
  {
    id: "chat",
    label: "채팅",
    items: [{ href: "/portfolio/chat", label: "Langchain과 대화하기" }],
  },
];

export default function LessonMobileDrawer() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const currentLabel = useMemo(() => {
    const hit = TOPICS.flatMap((topic) => topic.items).find(
      (it) => pathname === it.href || pathname.startsWith(`${it.href}/`)
    );
    return hit?.label ?? "메뉴";
  }, [pathname]);

  return (
    <div className="md:hidden">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-xs font-medium text-foreground/85 hover:bg-muted"
            aria-label="LESSON 메뉴 열기"
          >
            <Menu className="h-4 w-4" aria-hidden />
            {currentLabel}
          </button>
        </SheetTrigger>
        <SheetContent side="left" className="bg-background p-0">
          <SheetHeader className="border-b border-border">
            <SheetTitle className="text-sm tracking-[0.18em]">LESSON</SheetTitle>
          </SheetHeader>

          <div className="p-4">
            {TOPICS.map((topic) => (
              <div key={topic.id} className="mb-4 last:mb-0">
                <p className="mb-2 text-xs font-semibold tracking-[0.18em] text-muted-foreground">
                  {topic.label}
                </p>
                <nav className="space-y-1">
                  {topic.items.map((it) => {
                    const active = pathname === it.href || pathname.startsWith(`${it.href}/`);
                    return (
                      <Link
                        key={it.href}
                        href={it.href}
                        onClick={() => setOpen(false)}
                        className={cn(
                          "block rounded-md px-2 py-2 text-sm text-foreground/80 hover:bg-muted",
                          active && "bg-muted font-medium text-foreground"
                        )}
                      >
                        {it.label}
                      </Link>
                    );
                  })}
                </nav>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

