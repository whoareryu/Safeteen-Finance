import { Suspense } from "react";
import GourmetMateHero from "./gourmet-mate-hero";
import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="home-on-white home-apple-hero flex min-h-full flex-col">
      <Suspense fallback={<div className="gourmet-hero min-h-[12rem] w-full" aria-hidden />}>
        <GourmetMateHero />
      </Suspense>

      <div className="mx-auto w-full max-w-5xl bg-[#fbfbfd] px-4 pb-12 dark:bg-[#0a0a0a] sm:px-6">
        <SocialFooter />
      </div>
    </section>
  );
}
