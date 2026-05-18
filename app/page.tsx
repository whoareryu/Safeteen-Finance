import HeroSection from "@/components/hero-section";
import NeonFlowLines from "@/components/neon-flow-lines";

export default function Home() {
  return (
    <main className="home-main home-main--white relative h-[calc(100dvh-var(--site-header-height))] overflow-hidden bg-background">
      <NeonFlowLines embedded />
      <div className="home-content-layer">
        <HeroSection />
      </div>
    </main>
  );
}
