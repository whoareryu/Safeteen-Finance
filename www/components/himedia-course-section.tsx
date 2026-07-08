import PortfolioProjectTiles from "./portfolio-project-tiles";

export default function HimediaCourseSection() {
  return (
    <section
      id="himedia-course"
      className="w-full scroll-mt-[calc(var(--site-header-height)+1rem)]"
      aria-labelledby="himedia-course-title"
    >
      <div className="mx-auto w-full max-w-5xl text-center">
        <p className="mb-2 text-xs font-medium uppercase tracking-[0.22em] text-[#86868b]">
          Hi-Media Academy
        </p>
        <h2
          id="himedia-course-title"
          className="text-3xl font-semibold tracking-tight text-[#1d1d1f] md:text-4xl"
        >
          하이미디어 재직자 과정
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-base text-[#6e6e73] md:text-lg">
          프로젝트 포트폴리오 — 바로 아래에서 과정별 결과물을 확인하세요.
        </p>
      </div>

      <div className="mt-10">
        <PortfolioProjectTiles />
      </div>
    </section>
  );
}
