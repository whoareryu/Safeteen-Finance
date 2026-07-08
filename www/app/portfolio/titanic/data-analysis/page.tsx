import TitanicAnalysisChat from "@/components/titanic-analysis-chat";

export default function TitanicDataAnalysisPage() {
  return (
    <div className="space-y-6">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          2. 데이터 분석
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          업로드된 데이터의 요약/EDA를 정리하는 섹션입니다.
        </p>
      </header>

      <TitanicAnalysisChat />
    </div>
  );
}

