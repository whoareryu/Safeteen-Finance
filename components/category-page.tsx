import type { NavCategory } from "@/lib/navigation";
import CategoryBrowse from "@/components/category-browse";

export default function CategoryPage({ category }: { category: NavCategory }) {
  return <CategoryBrowse category={category} />;
}
