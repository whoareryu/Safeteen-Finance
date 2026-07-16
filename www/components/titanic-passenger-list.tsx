"use client";

import { useEffect, useMemo, useState } from "react";

const PAGE_SIZE = 100;

type PassengerRow = {
  passenger_id?: string | number;
  PassengerId?: string | number;
  name?: string;
  Name?: string;
  gender?: string;
  Sex?: string;
  pclass?: string | number;
  Pclass?: string | number;
  survived?: string | number;
  Survived?: string | number;
  age?: string | number | null;
  Age?: string | number | null;
};

function asText(value: unknown): string {
  if (value == null) return "-";
  const text = String(value).trim();
  return text || "-";
}

export default function PassengerList() {
  const [rows, setRows] = useState<PassengerRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/titanic/walter/myself", {
          cache: "no-store",
        });
        const payload = (await res.json().catch(() => null)) as { detail?: string } | null;
        if (!res.ok) {
          throw new Error(payload?.detail ?? "승객 명단 조회에 실패했습니다.");
        }
        if (cancelled) return;
        setRows([]);
        setTotal(0);
      } catch (e) {
        if (cancelled) return;
        setRows([]);
        setTotal(0);
        setError(e instanceof Error ? e.message : "승객 명단 조회 중 오류가 발생했습니다.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const totalPages = useMemo(() => {
    if (!total) return 1;
    return Math.ceil(total / PAGE_SIZE);
  }, [total]);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  return (
    <section className="overflow-hidden rounded-2xl border border-border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3">
        <p className="text-sm text-foreground">
          전체 승객 <span className="font-semibold">{total.toLocaleString()}</span>명
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-md border border-border px-3 py-1.5 text-sm disabled:opacity-50"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            이전
          </button>
          <span className="text-sm text-foreground">
            {page} / {totalPages}
          </span>
          <button
            type="button"
            className="rounded-md border border-border px-3 py-1.5 text-sm disabled:opacity-50"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            다음
          </button>
        </div>
      </div>

      {loading ? (
        <p className="px-4 py-6 text-sm text-muted-foreground">승객 명단을 불러오는 중입니다...</p>
      ) : error ? (
        <p className="px-4 py-6 text-sm text-red-700">{error}</p>
      ) : rows.length === 0 ? (
        <p className="px-4 py-6 text-sm text-muted-foreground">
          저장된 승객 데이터가 없습니다. 먼저 CSV를 업로드해 주세요.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-muted text-foreground">
              <tr>
                <th className="px-4 py-2 font-medium">PassengerId</th>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Gender</th>
                <th className="px-4 py-2 font-medium">Pclass</th>
                <th className="px-4 py-2 font-medium">Survived</th>
                <th className="px-4 py-2 font-medium">Age</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={`${asText(row.passenger_id ?? row.PassengerId)}-${idx}`} className="border-t border-border">
                  <td className="px-4 py-2">{asText(row.passenger_id ?? row.PassengerId)}</td>
                  <td className="px-4 py-2">{asText(row.name ?? row.Name)}</td>
                  <td className="px-4 py-2">{asText(row.gender ?? row.Sex)}</td>
                  <td className="px-4 py-2">{asText(row.pclass ?? row.Pclass)}</td>
                  <td className="px-4 py-2">{asText(row.survived ?? row.Survived)}</td>
                  <td className="px-4 py-2">{asText(row.age ?? row.Age)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

