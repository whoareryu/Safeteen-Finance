import PlantPhotoUpload from "@/components/plant-photo-upload";

export default function PlantPage() {
  return (
    <div>
      <section className="saessak-photo-hero saessak-photo-hero--banner relative flex items-end overflow-hidden px-6 pb-8 pt-14">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1667395941567-9892435d0240?w=1600&q=80&auto=format&fit=crop"
          alt=""
          aria-hidden
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="saessak-photo-scrim absolute inset-0" aria-hidden />
        <div className="relative mx-auto max-w-2xl">
          <h1 className="text-2xl font-semibold text-white sm:text-3xl">AI 잎사귀 진단</h1>
          <p className="mt-1 text-sm text-white/85">
            잎사귀 사진 한 장이면 품종과 병징을 바로 알려드려요.
          </p>
        </div>
      </section>
      <div className="mx-auto max-w-2xl px-6 py-10">
        <PlantPhotoUpload />
      </div>
    </div>
  );
}
