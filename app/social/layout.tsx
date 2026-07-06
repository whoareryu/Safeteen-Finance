"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mail, MessageSquare, Send } from "lucide-react";
import { cn } from "@/lib/utils";

const SUB_TABS = [
  { href: "/social/mail",     label: "메일",     Icon: Mail },
  { href: "/social/discord",  label: "디스코드", Icon: MessageSquare },
  { href: "/social/telegram", label: "텔레그램", Icon: Send },
] as const;

export default function SocialLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col">
      {/* 서브탭 바 */}
      <div className="sticky top-14 z-30 border-b border-border bg-background/95 backdrop-blur">
        <nav className="mx-auto flex max-w-4xl overflow-x-auto px-4">
          {SUB_TABS.map(({ href, label, Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex shrink-0 items-center gap-1.5 whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition",
                  active
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" aria-hidden />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* 페이지 콘텐츠 */}
      {children}
    </div>
  );
}
