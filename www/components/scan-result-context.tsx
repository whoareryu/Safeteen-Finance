"use client";

import { createContext, useContext, useState } from "react";
import type { AnalysisResult } from "@/lib/safeteen-api";

type ScanResultContextValue = {
  result: AnalysisResult | null;
  setResult: (result: AnalysisResult | null) => void;
  /** 방금 스캐너에서 넘어온 결과인지 — DANGER 진입 모달을 한 번만 띄우기 위한 플래그. */
  justScanned: boolean;
  consumeJustScanned: () => void;
};

const ScanResultContext = createContext<ScanResultContextValue | null>(null);

export function ScanResultProvider({ children }: { children: React.ReactNode }) {
  const [result, setResultState] = useState<AnalysisResult | null>(null);
  const [justScanned, setJustScanned] = useState(false);

  function setResult(next: AnalysisResult | null) {
    setResultState(next);
    setJustScanned(next !== null);
  }

  function consumeJustScanned() {
    setJustScanned(false);
  }

  return (
    <ScanResultContext.Provider value={{ result, setResult, justScanned, consumeJustScanned }}>
      {children}
    </ScanResultContext.Provider>
  );
}

export function useScanResult() {
  const ctx = useContext(ScanResultContext);
  if (!ctx) throw new Error("useScanResult는 ScanResultProvider 안에서만 사용할 수 있습니다.");
  return ctx;
}
