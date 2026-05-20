import BrowseShellLayout from "@/components/browse-shell-layout";
import CategoryBrowse from "@/components/category-browse";
import type { NavCategory } from "@/lib/navigation";

export default function CategoryPage({ category }: { category: NavCategory }) {
  return (
    <BrowseShellLayout>
      <CategoryBrowse category={category} />
    </BrowseShellLayout>
  );
}
