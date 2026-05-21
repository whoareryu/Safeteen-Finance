import PortfolioProjectTiles from "@/components/portfolio-project-tiles";

export default function PortfolioPage() {
  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))] bg-[#fbfbfd]">
      <section className="border-b border-black/[0.06] bg-[#f5f5f7] px-6 py-16 text-center md:py-24">
        <p className="text-xs font-medium uppercase tracking-[0.22em] text-[#86868b]">
          Hi-Media Academy · 수업용
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-[#1d1d1f] md:text-5xl">
          하이미디어 재직자 과정
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-[#6e6e73]">
          과정에서 진행한 프로젝트를 선택해 상세 화면으로 이동합니다.
        </p>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-12 md:px-6 md:py-16">
        <PortfolioProjectTiles large />
      </section>
    </main>
  );
}
