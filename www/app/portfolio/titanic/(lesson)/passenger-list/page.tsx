import PassengerList from "@/components/titanic-passenger-list";

export default function PassengerListPage() {
  return (
    <div className="space-y-6">
      <header className="pt-1">
        <h1 className="text-2xl font-semibold leading-snug tracking-tight text-foreground">
          2. 탑승자 목록
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          업로드한 승객 데이터를 확인합니다. 한 페이지에 100명씩 표시됩니다.
        </p>
      </header>

      <PassengerList />
    </div>
  );
}

