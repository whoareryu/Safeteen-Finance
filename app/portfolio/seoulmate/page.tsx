import Link from "next/link";

export default function SeoulMatePage() {
  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-[#fbfbfd]">
      <section className="relative flex min-h-[50vh] flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-[#1a0a2e] via-[#3d1a6e] to-[#0f4c5c] px-6 py-20 text-center text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse 80% 50% at 50% 100%, rgba(236,72,153,0.4) 0%, transparent 55%)",
          }}
          aria-hidden
        />
        <p className="relative z-10 text-sm font-medium text-white/70">Portfolio</p>
        <h1 className="relative z-10 mt-2 text-4xl font-semibold md:text-6xl">SeoulMate</h1>
        <p className="relative z-10 mt-4 max-w-lg text-lg text-white/85">
          서울 탐험 AI 동반 프로젝트 — 맛집, 명소, 코스 추천을 준비 중입니다.
        </p>
      </section>
      <div className="mx-auto max-w-3xl px-6 py-12 text-center">
        <Link href="/portfolio" className="apple-cta-primary inline-flex rounded-full px-6 py-2.5 text-sm">
          Portfolio로
        </Link>
      </div>
    </main>
  );
}
