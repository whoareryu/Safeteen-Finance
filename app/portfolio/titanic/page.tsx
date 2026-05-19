import Link from "next/link";

export default function TitanicPage() {
  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-[#fbfbfd]">
      <section className="relative flex min-h-[50vh] flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-[#0c1929] via-[#1e3a5f] to-[#0a1628] px-6 py-20 text-center text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse 70% 45% at 50% 110%, rgba(56,189,248,0.35) 0%, transparent 50%)",
          }}
          aria-hidden
        />
        <p className="relative z-10 text-sm font-medium text-white/70">Portfolio</p>
        <h1 className="relative z-10 mt-2 text-4xl font-semibold md:text-6xl">타이타닉</h1>
        <p className="relative z-10 mt-4 max-w-lg text-lg text-white/85">
          승객 데이터 분석·생존 예측 모델 — 대시보드와 API 연동을 준비 중입니다.
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
