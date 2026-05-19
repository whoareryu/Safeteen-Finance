import GourmetMateHero from "./gourmet-mate-hero";
import HimediaCourseSection from "./himedia-course-section";
import GeminiChat from "./gemini-chat";
import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="home-on-white home-apple-hero flex min-h-full flex-col bg-[#fbfbfd] px-4 pb-12 pt-6 sm:px-6 md:pt-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center gap-10 md:gap-14">
        <GourmetMateHero />

        <div className="w-full border-t border-black/[0.06] pt-10">
          <p className="mb-6 text-center text-xs font-medium uppercase tracking-[0.2em] text-[#86868b]">
            AI에게 바로 물어보기
          </p>
          <div className="home-apple-chat mx-auto w-full max-w-3xl">
            <GeminiChat variant="apple" />
          </div>
        </div>

        <HimediaCourseSection />

        <div className="mx-auto w-full max-w-5xl">
          <SocialFooter />
        </div>
      </div>
    </section>
  );
}
