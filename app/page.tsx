import HeroSection from "@/components/hero-section";
import NeonFlowLines from "@/components/neon-flow-lines";

export default function Home() {
  return (
    <main className="home-main home-main--white relative h-screen overflow-hidden bg-white">
      <NeonFlowLines embedded />
      <div className="relative z-10">
        <HeroSection />
      </div>
    </main>
  );
}
