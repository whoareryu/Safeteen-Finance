import Link from "next/link";
import PlantPhotoUpload from "@/components/plant-photo-upload";

export default function Home() {
  return (
    <main className="home-main min-h-[calc(100dvh-var(--site-header-height))]">
      <section className="mx-auto max-w-2xl px-6 py-10 text-center">
        <p className="text-sm font-medium text-[#0071e3]">방구석 플랜트 매니저</p>
        <h1 className="mt-2 text-3xl font-semibold text-[#1d1d1f]">
          잎사귀 사진 한 장으로 시작하는 반려식물 케어
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-[#6e6e73]">
          품종·증상 진단부터 날씨 기반 물주기 알림까지, AI 에이전트가 초보 식집사를 도와드려요.
        </p>
        <Link
          href="/plant/care-calendar"
          className="mt-4 inline-block text-sm text-[#0071e3] underline underline-offset-4"
        >
          내 식물 케어 일정 보기 →
        </Link>
      </section>

      <section className="mx-auto max-w-2xl px-6 pb-10">
        <PlantPhotoUpload />
      </section>
    </main>
  );
}
