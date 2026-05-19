import { notFound } from "next/navigation";
import CategoryPage from "@/components/category-page";
import { CATEGORY_LINKS, getCategoryBySlug } from "@/lib/navigation";

export function generateStaticParams() {
  return CATEGORY_LINKS.map((c) => ({ slug: c.slug }));
}

export default async function FoodCategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = getCategoryBySlug(slug);
  if (!category) notFound();
  return <CategoryPage category={category} />;
}
