export default function VisionPage() {
  return (
    <div className="min-h-[calc(100dvh-var(--site-header-height))] bg-background">
      <section className="relative flex min-h-[36vh] flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-[#0c1929] via-[#1e3a5f] to-[#0a1628] px-6 py-14 text-center text-white md:py-16">
        <div
          className="pointer-events-none absolute inset-0 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse 70% 45% at 50% 110%, rgba(56,189,248,0.35) 0%, transparent 50%)",
          }}
          aria-hidden
        />
        <p className="relative z-10 text-sm font-medium text-white/70">수업용</p>
        <h1 className="relative z-10 mt-2 text-4xl font-semibold md:text-5xl">Vision</h1>
        <p className="relative z-10 mt-4 max-w-lg text-base text-white/85 md:text-lg">
          이미지 업로드 → 비전 처리 파이프라인. 왼쪽 메뉴에서 단계를 선택하세요.
        </p>
      </section>
    </div>
  );
}
