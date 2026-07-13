"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import PlantCareCalendarList from "@/components/plant-care-calendar-list";

function PlantCareCalendarContent() {
  const searchParams = useSearchParams();
  const plantId = Number(searchParams.get("plantId") ?? "1");
  const region = searchParams.get("region") ?? "서울";

  return <PlantCareCalendarList plantId={plantId} region={region} />;
}

export default function PlantCareCalendarPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Suspense fallback={<p className="text-sm text-[#86868b]">불러오는 중…</p>}>
        <PlantCareCalendarContent />
      </Suspense>
    </div>
  );
}
