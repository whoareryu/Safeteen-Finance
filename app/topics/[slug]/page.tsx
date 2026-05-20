import { notFound } from "next/navigation";
import BrowseShellLayout from "@/components/browse-shell-layout";
import TopicBrowsePage from "@/components/topic-browse-page";
import { HOME_TOPIC_LINKS, getTopicBySlug } from "@/lib/gourmet-topics";

export function generateStaticParams() {
  return HOME_TOPIC_LINKS.map((t) => ({ slug: t.slug }));
}

export default async function TopicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const topic = getTopicBySlug(slug);
  if (!topic) notFound();

  return (
    <BrowseShellLayout>
      <TopicBrowsePage topic={topic} />
    </BrowseShellLayout>
  );
}
