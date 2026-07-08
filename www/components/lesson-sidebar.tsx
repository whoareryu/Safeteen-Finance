"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
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
];

export default function LessonSidebar() {
  const pathname = usePathname();
  const active = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <aside className="relative z-20 hidden w-[260px] shrink-0 overflow-hidden border-r border-black/[0.06] bg-[#fbfbfd] md:block">
      <div className="sticky top-[var(--site-header-height)] max-h-[calc(100dvh-var(--site-header-height))] overflow-y-auto p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#6e6e73]">
          LESSON
        </p>

        <Accordion type="single" collapsible defaultValue="titanic">
          {TOPICS.map((topic) => (
            <AccordionItem key={topic.id} value={topic.id} className="border-0">
              <AccordionTrigger className="rounded-md px-2 py-2 text-sm hover:bg-black/[0.04] hover:no-underline [&>svg]:text-[#86868b]">
                <span className="font-medium text-[#1d1d1f]">{topic.label}</span>
              </AccordionTrigger>
              <AccordionContent className="pb-0">
                <nav className="mt-1 space-y-1">
                  {topic.items.map((it) => (
                    <Link
                      key={it.href}
                      href={it.href}
                      className={cn(
                        "block whitespace-nowrap rounded-md px-2 py-2 text-sm text-[#1d1d1f]/80 hover:bg-black/[0.04]",
                        active(it.href) && "bg-black/[0.06] font-medium text-[#1d1d1f]"
                      )}
                    >
                      {it.label}
                    </Link>
                  ))}
                </nav>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </aside>
  );
}

