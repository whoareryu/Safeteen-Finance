import HimediaCoursePicker from "./himedia-course-picker";
import GeminiChat from "./gemini-chat";
import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="home-on-white home-apple-hero flex h-full min-h-0 flex-col overflow-hidden px-6 pb-6 pt-2 sm:pt-4">
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center overflow-y-auto py-4">
        <div className="mx-auto flex w-full max-w-3xl flex-col items-center gap-8">
          <div className="flex w-full shrink-0 flex-col items-center text-center">
            <p className="neon-text-shield mb-3 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground md:text-sm">
              Architecture · AI Systems · Delivery
            </p>

            <h1 className="mb-5 text-balance text-3xl font-bold leading-[1.15] md:text-4xl lg:text-5xl xl:text-6xl">
              <span className="neon-gradient-title">
                <span className="neon-gradient-title__underlay" aria-hidden>
                  Modular Monolith
                </span>
                <span className="neon-gradient-title__gradient bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 dark:from-purple-400 dark:via-pink-500 dark:to-cyan-400">
                  Modular Monolith
                </span>
              </span>
              <br />
              <span className="neon-text-shield mt-2 block text-2xl font-semibold text-foreground md:text-3xl lg:text-4xl">
                모듈러 모노리식 아키텍처
              </span>
            </h1>

            <p className="neon-text-shield mx-auto mb-3 max-w-2xl text-pretty text-base leading-relaxed text-muted-foreground md:text-lg">
              도메인 경계를 모듈로 쪼개고,{" "}
              <span className="font-medium text-foreground">하나의 배포 단위</span>로
              묶습니다. 결합은 낮추고 응집은 높여 — 확장과 변경이 예측 가능한 구조를
              설계합니다.
            </p>

            <p className="neon-text-shield mx-auto max-w-xl text-pretty text-sm leading-relaxed text-muted-foreground/90 md:text-base">
              <span className="font-medium text-primary">클린 아키텍처</span> 원칙과
              명시적 포트·어댑터로 비즈니스 로직을 보호하고, 읽기 쉬운 코드로{" "}
              <span className="font-medium text-primary">지속 가능한 개발</span>을 이어
              갑니다.
            </p>
          </div>

          <HimediaCoursePicker />

          <div className="home-apple-chat flex min-h-[min(28vh,240px)] w-full flex-col justify-center text-left md:min-h-[min(26vh,280px)]">
            <GeminiChat variant="apple" />
          </div>
        </div>
      </div>

      <div className="home-apple-footer shrink-0">
        <SocialFooter />
      </div>
    </section>
  );
}
