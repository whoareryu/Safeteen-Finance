import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="flex h-screen flex-col items-center justify-between overflow-hidden px-6 pb-6 pt-20">
      <div className="mx-auto flex max-w-3xl flex-1 flex-col items-center justify-center text-center">
        <p className="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground md:text-sm">
          Architecture · AI Systems · Delivery
        </p>

        <h1 className="mb-5 text-balance text-3xl font-bold leading-[1.15] md:text-4xl lg:text-5xl xl:text-6xl">
          <span className="bg-gradient-to-r from-purple-300 via-pink-400 to-cyan-300 bg-clip-text text-transparent dark:from-purple-400 dark:via-pink-500 dark:to-cyan-400">
            Modular Monolith
          </span>
          <br />
          <span className="mt-2 inline-block text-2xl font-semibold text-foreground md:text-3xl lg:text-4xl">
            모듈러 모노리식 아키텍처
          </span>
        </h1>

        <p className="mx-auto mb-3 max-w-2xl text-pretty text-base leading-relaxed text-muted-foreground md:text-lg">
          도메인 경계를 모듈로 쪼개고,{" "}
          <span className="font-medium text-foreground">하나의 배포 단위</span>로 묶습니다.
          결합은 낮추고 응집은 높여 — 확장과 변경이 예측 가능한 구조를 설계합니다.
        </p>

        <p className="mx-auto mb-6 max-w-xl text-pretty text-sm leading-relaxed text-muted-foreground/90 md:text-base">
          <span className="font-medium text-primary">클린 아키텍처</span> 원칙과 명시적 포트·어댑터로
          비즈니스 로직을 보호하고, 읽기 쉬운 코드로{" "}
          <span className="font-medium text-primary">지속 가능한 개발</span>을 이어 갑니다.
        </p>

        <p className="mx-auto max-w-2xl text-pretty border-t border-border/50 pt-6 text-sm leading-relaxed text-muted-foreground md:text-base">
          앞으로의 AI 개발은 <span className="font-medium text-foreground">추론·RAG·에이전트</span>를
          제품의 한 레이어로 편입시키되,{" "}
          <span className="font-medium text-primary">하네스와 계약</span>으로 행동과 데이터를 묶습니다.
          모델은 바뀌어도 도메인 경계와 관측 가능한 파이프라인은 유지 —{" "}
          <span className="font-medium text-foreground">미래지향적인 AI 시스템</span>을
          안전하게 진화시키는 것이 목표입니다.
        </p>
      </div>

      <SocialFooter />
    </section>
  );
}
