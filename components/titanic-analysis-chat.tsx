"use client";

import { useEffect, useMemo, useState } from "react";

type TitanicRow = {
  PassengerId: number;
  Survived: number;
  Pclass: number;
  Name: string;
  Sex: string;
  Age: number | null;
};

const TITANIC_LOCAL_KEY = "titanic_csv_rows_v1";

type ChatMsg = { role: "user" | "assistant"; content: string };

function pct(n: number) {
  return `${(n * 100).toFixed(1)}%`;
}

function summarize(rows: TitanicRow[]) {
  const total = rows.length;
  const survived = rows.filter((r) => r.Survived === 1).length;
  const survivalRate = total ? survived / total : 0;

  const bySex = ["male", "female"].map((sex) => {
    const group = rows.filter((r) => (r.Sex ?? "").toLowerCase() === sex);
    const t = group.length;
    const s = group.filter((r) => r.Survived === 1).length;
    return { sex, total: t, survived: s, rate: t ? s / t : 0 };
  });

  const byClass = [1, 2, 3].map((pclass) => {
    const group = rows.filter((r) => r.Pclass === pclass);
    const t = group.length;
    const s = group.filter((r) => r.Survived === 1).length;
    return { pclass, total: t, survived: s, rate: t ? s / t : 0 };
  });

  const ages = rows.map((r) => r.Age).filter((a): a is number => typeof a === "number");
  const avgAge = ages.length ? ages.reduce((a, b) => a + b, 0) / ages.length : null;
  const missingAge = rows.filter((r) => r.Age == null).length;

  return { total, survived, survivalRate, bySex, byClass, avgAge, missingAge };
}

function answer(rows: TitanicRow[], q: string): string {
  const s = summarize(rows);
  const text = q.trim().toLowerCase();

  if (!text) return "질문을 입력해 주세요.";

  if (text.includes("전체") || text.includes("총") || text.includes("승객 수")) {
    return `총 승객 수는 ${s.total}명이고, 생존자는 ${s.survived}명입니다. 생존률은 ${pct(
      s.survivalRate
    )} 입니다.`;
  }

  if (text.includes("생존률") || text.includes("생존")) {
    if (text.includes("성별") || text.includes("남") || text.includes("여")) {
      const m = s.bySex.find((x) => x.sex === "male")!;
      const f = s.bySex.find((x) => x.sex === "female")!;
      return `성별 생존률:\n- 남성: ${m.survived}/${m.total} (${pct(m.rate)})\n- 여성: ${f.survived}/${f.total} (${pct(f.rate)})`;
    }
    if (text.includes("등급") || text.includes("pclass") || text.includes("1등") || text.includes("2등") || text.includes("3등")) {
      return `객실 등급별 생존률:\n- 1등급: ${s.byClass[0]!.survived}/${s.byClass[0]!.total} (${pct(s.byClass[0]!.rate)})\n- 2등급: ${s.byClass[1]!.survived}/${s.byClass[1]!.total} (${pct(s.byClass[1]!.rate)})\n- 3등급: ${s.byClass[2]!.survived}/${s.byClass[2]!.total} (${pct(s.byClass[2]!.rate)})`;
    }
    return `전체 생존률은 ${pct(s.survivalRate)} 입니다. (생존 ${s.survived}/${s.total})`;
  }

  if (text.includes("나이") || text.includes("age")) {
    const avg = s.avgAge == null ? "알 수 없음" : `${s.avgAge.toFixed(1)}세`;
    return `나이 정보:\n- 평균 나이: ${avg}\n- 나이 결측치: ${s.missingAge}명`;
  }

  return [
    "이 분석 채팅은 Titanic CSV 결과만 답합니다.",
    "추천 질문:",
    "- 전체 승객 수/생존률",
    "- 성별 생존률",
    "- 등급별 생존률",
    "- 나이 평균/결측치",
  ].join("\n");
}

export default function TitanicAnalysisChat() {
  const [rows, setRows] = useState<TitanicRow[] | null>(null);
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      role: "assistant",
      content:
        "Titanic 분석 전용 채팅입니다. 업로드한 CSV 기준으로만 결과를 답합니다.\n예: “전체 생존률 알려줘”, “성별 생존률”",
    },
  ]);
  const [input, setInput] = useState("");

  useEffect(() => {
    try {
      const raw = localStorage.getItem(TITANIC_LOCAL_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as TitanicRow[];
      if (Array.isArray(parsed) && parsed.length > 0) setRows(parsed);
    } catch {
      // ignore
    }
  }, []);

  const summary = useMemo(() => (rows ? summarize(rows) : null), [rows]);

  const send = () => {
    if (!rows) {
      setMessages((prev) => [
        ...prev,
        { role: "user", content: input || "(빈 질문)" },
        {
          role: "assistant",
          content:
            "아직 CSV 데이터가 없습니다. 먼저 `1. 데이터 수집`에서 CSV를 저장해 주세요.",
        },
      ]);
      setInput("");
      return;
    }
    const q = input.trim();
    if (!q) return;
    const a = answer(rows, q);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: q },
      { role: "assistant", content: a },
    ]);
    setInput("");
  };

  return (
    <div className="min-w-0 rounded-2xl border border-black/[0.06] bg-white p-4 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#86868b]">
            TITANIC · ANALYSIS CHAT
          </p>
          {summary ? (
            <p className="mt-1 text-xs text-[#6e6e73]">
              {summary.total}명 · 생존률 {pct(summary.survivalRate)}
            </p>
          ) : (
            <p className="mt-1 text-xs text-[#6e6e73]">
              CSV가 없으면 답변할 수 없습니다.
            </p>
          )}
        </div>
      </div>

      <div className="max-h-[360px] space-y-3 overflow-auto rounded-xl bg-[#fbfbfd] p-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "ml-auto w-fit max-w-[90%] rounded-2xl bg-black/[0.06] px-3 py-2 text-sm text-[#1d1d1f]"
                : "mr-auto w-fit max-w-[90%] whitespace-pre-wrap rounded-2xl bg-white px-3 py-2 text-sm text-[#1d1d1f]/90 shadow-sm ring-1 ring-black/[0.06]"
            }
          >
            {m.content}
          </div>
        ))}
      </div>

      <div className="mt-3 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-stretch">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
          placeholder="예: 성별 생존률 알려줘"
          className="min-w-0 flex-1 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black/10"
        />
        <button
          type="button"
          onClick={send}
          className="shrink-0 self-end whitespace-nowrap rounded-xl bg-black px-3 py-2 text-xs font-medium text-white hover:bg-black/90 sm:self-auto"
        >
          전송
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {[
          "전체 승객 수/생존률",
          "성별 생존률",
          "등급별 생존률",
          "나이 평균/결측치",
        ].map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => setInput(q)}
            className="rounded-full bg-black/[0.04] px-3 py-1.5 text-xs text-[#1d1d1f]/80 hover:bg-black/[0.06]"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

