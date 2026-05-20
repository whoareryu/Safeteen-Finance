import GourmetMateHero from "./gourmet-mate-hero";
import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="home-on-white home-apple-hero flex min-h-full flex-col">
      <GourmetMateHero />

      <div className="mx-auto w-full max-w-5xl bg-[#fbfbfd] px-4 pb-12 sm:px-6">
        <SocialFooter />
      </div>
    </section>
  );
}
