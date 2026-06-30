import TodayRecommendation from "@/components/today-recommendation";
import TopicFeed from "@/components/topic-feed";

export default function Home() {
  return (
    <main className="home-main min-h-[calc(100dvh-var(--site-header-height))]">
      <TodayRecommendation />
      <TopicFeed />
    </main>
  );
}
