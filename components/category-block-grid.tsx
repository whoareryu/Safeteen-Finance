import Link from "next/link";
import { CATEGORY_LINKS } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type CategoryBlockGridProps = {
  className?: string;
  title?: string;
};

export default function CategoryBlockGrid({
  className,
  title = "음식 장르별 탐색",
}: CategoryBlockGridProps) {
  return (
    <div className={cn("w-full", className)}>
      {title ? (
        <p className="mb-4 text-center text-sm font-medium text-[#6e6e73] md:text-base">
          {title}
        </p>
      ) : null}

      <div className="-mx-1 overflow-x-auto pb-2 md:overflow-visible">
        <div className="flex min-w-min gap-3 px-1 md:grid md:min-w-0 md:grid-cols-4 md:gap-4 lg:grid-cols-8">
          {CATEGORY_LINKS.map((cat) => (
            <Link
              key={cat.slug}
              href={cat.href}
              className={cn(
                "group relative flex h-[92px] w-[108px] shrink-0 flex-col items-center justify-center gap-1 overflow-hidden rounded-xl border-2 px-2 py-3 shadow-md transition duration-200 hover:-translate-y-1 hover:shadow-lg md:h-[100px] md:w-auto",
                cat.block.bg,
                cat.block.hoverBg,
                cat.block.border,
                cat.block.text
              )}
            >
              <span
                className="pointer-events-none absolute -right-1 -top-2 text-5xl opacity-[0.12] transition group-hover:opacity-20"
                aria-hidden
              >
                {cat.block.emoji}
              </span>
              <span className="relative text-2xl drop-shadow-sm" aria-hidden>
                {cat.block.emoji}
              </span>
              <span className="relative text-center text-xs font-bold leading-tight tracking-tight md:text-sm">
                {cat.label}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
