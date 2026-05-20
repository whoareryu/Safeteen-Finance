import BrowseShellLayout from "@/components/browse-shell-layout";
import HeroSection from "@/components/hero-section";

export default function Home() {
  return (
    <main className="home-main min-h-[calc(100dvh-var(--site-header-height))]">
      <BrowseShellLayout>
        <HeroSection />
      </BrowseShellLayout>
    </main>
  );
}
