import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PORTFOLIO_LINKS } from "@/lib/navigation";

const TILE_STYLES = {
  seoulmate: {
    gradient:
      "bg-gradient-to-br from-[#1a0a2e] via-[#3d1a6e] to-[#0f4c5c]",
    pattern:
      "radial-gradient(ellipse 80% 50% at 50% 100%, rgba(236,72,153,0.35) 0%, transparent 55%), radial-gradient(circle at 85% 15%, rgba(34,211,238,0.25) 0%, transparent 40%)",
    glow: "shadow-[0_24px_80px_-12px_rgba(168,85,247,0.45)]",
    icon: "🏙️",
    description:
      "서울 여행·맛집·명소를 AI와 함께 탐색하는 서울 메이트 프로젝트입니다.",
  },
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
} as const;

export default function PortfolioProjectTiles({ large = false }: { large?: boolean }) {
  return (
    <div
      className={`grid gap-4 ${large ? "lg:grid-cols-2" : "sm:grid-cols-2"} sm:gap-5`}
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
