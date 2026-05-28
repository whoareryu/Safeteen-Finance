import TitanicPassengerList from "@/components/titanic-passenger-list";

export default function TitanicPassengerListPage() {
  return (
    <div className="space-y-6">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-[#1d1d1f]">
          4. 승객 명단
        </h1>
        <p className="mt-2 text-sm text-[#6e6e73]">
          업로드한 승객 데이터를 확인합니다. 한 페이지에 100명씩 표시됩니다.
        </p>
      </header>

      <TitanicPassengerList />
    </div>
  );
}

