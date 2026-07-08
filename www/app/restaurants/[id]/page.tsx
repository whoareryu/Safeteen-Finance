import { notFound } from "next/navigation";
import RestaurantDetailPage from "@/components/restaurant-detail-page";

export default async function RestaurantPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const restaurantId = Number(id);
  if (!Number.isInteger(restaurantId) || restaurantId < 1) {
    notFound();
  }

  return <RestaurantDetailPage restaurantId={restaurantId} />;
}
