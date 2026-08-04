import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PORTFOLIO_LINKS } from "@/lib/navigation";

const TILE_STYLES = {
  titanic: {
    gradient:
      "bg-gradient-to-br from-[#0c1929] via-[#1e3a5f] to-[#0a1628]",
    pattern:
      "radial-gradient(ellipse 70% 45% at 50% 110%, rgba(56,189,248,0.3) 0%, transparent 50%), linear-gradient(180deg, transparent 60%, rgba(15,23,42,0.8) 100%)",
    glow: "shadow-[0_24px_80px_-12px_rgba(37,99,235,0.4)]",
    icon: "🚢",
    description:
      "타이타닉 승객 데이터로 생존을 예측하는 머신러닝·데이터 분석 프로젝트입니다.",
  },
  ledger: {
    gradient:
      "bg-gradient-to-br from-[#0c291f] via-[#1e5f3a] to-[#0a2818]",
    pattern:
      "radial-gradient(ellipse 70% 45% at 50% 110%, rgba(52,211,153,0.3) 0%, transparent 50%), linear-gradient(180deg, transparent 60%, rgba(15,42,23,0.8) 100%)",
    glow: "shadow-[0_24px_80px_-12px_rgba(16,185,129,0.4)]",
    icon: "📒",
    description:
      "매일의 수입·지출을 기록하고 카테고리별 지출 흐름을 한눈에 보여주는 가계부 웹 애플리케이션입니다.",
  },
} as const;

export default function PortfolioProjectTiles({ large = false }: { large?: boolean }) {
  return (
    <div
      className={`grid gap-4 ${large ? "max-w-xl mx-auto" : "max-w-md mx-auto"} sm:gap-5`}
    >
      {PORTFOLIO_LINKS.map((item) => {
        const style = TILE_STYLES[item.theme];
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`apple-product-tile group relative flex flex-col justify-end overflow-hidden rounded-2xl p-6 text-left md:p-10 ${style.gradient} ${style.glow} transition-transform duration-300 hover:scale-[1.01] ${large ? "min-h-[320px] md:min-h-[420px]" : "min-h-[220px] md:min-h-[280px]"}`}
          >
            <div
              className="pointer-events-none absolute inset-0"
              style={{ background: style.pattern }}
              aria-hidden
            />
            <div
              className="pointer-events-none absolute -right-6 -top-6 text-[6rem] opacity-20 md:text-[9rem]"
              aria-hidden
            >
              {style.icon}
            </div>
            <div className="relative z-10 max-w-md">
              <p className="text-sm font-medium text-white/70">{item.tagline}</p>
              <h3 className="mt-1 text-3xl font-semibold tracking-tight text-white md:text-4xl">
                {item.label}
              </h3>
              {large ? (
                <p className="mt-3 text-base leading-relaxed text-white/80">
                  {style.description}
                </p>
              ) : null}
              <span className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-white/90">
                프로젝트 보기
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
