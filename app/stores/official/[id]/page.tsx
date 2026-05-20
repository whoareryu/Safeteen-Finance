import { redirect } from "next/navigation";

/** 구 URL 호환 — 상세는 ``/restaurants/[id]`` 로 통합 */
export default async function LegacyOfficialStoreRedirect({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  redirect(`/restaurants/${id}`);
}
