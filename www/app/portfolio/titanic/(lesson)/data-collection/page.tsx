import TitanicDataUpload from "@/components/titanic-data-upload";

export default function TitanicDataCollectionPage() {
  return (
    <div className="space-y-6">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          1. 데이터 수집
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          타이타닉 CSV 업로드/확인 단계를 진행합니다.
        </p>
      </header>

      <TitanicDataUpload showHeading={false} />
    </div>
  );
}

