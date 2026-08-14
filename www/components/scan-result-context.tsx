"use client";

import { createContext, useContext, useState } from "react";
import type { AnalysisResult } from "@/lib/safeteen-api";

type ScanResultContextValue = {
  result: AnalysisResult | null;
  setResult: (result: AnalysisResult | null) => void;
};

const ScanResultContext = createContext<ScanResultContextValue | null>(null);

export function ScanResultProvider({ children }: { children: React.ReactNode }) {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  return <ScanResultContext.Provider value={{ result, setResult }}>{children}</ScanResultContext.Provider>;
}

export function useScanResult() {
  const ctx = useContext(ScanResultContext);
  if (!ctx) throw new Error("useScanResult는 ScanResultProvider 안에서만 사용할 수 있습니다.");
  return ctx;
}
