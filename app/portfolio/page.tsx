import Header from "@/components/header";
import AgentsSection from "@/components/agents-section";

export default function PortfolioPage() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <div className="pt-20">
        <AgentsSection />
      </div>
    </main>
  );
}
