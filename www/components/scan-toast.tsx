"use client";

import { createContext, useCallback, useContext, useRef, useState } from "react";

type ToastContextValue = {
  notify: (message: string) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ScanToastProvider({ children }: { children: React.ReactNode }) {
  const [message, setMessage] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const notify = useCallback((next: string) => {
    setMessage(next);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setMessage(null), 2600);
  }, []);

  return (
    <ToastContext.Provider value={{ notify }}>
      {children}
      {message && (
        <div className="fixed bottom-7 left-1/2 z-[70] -translate-x-1/2 rounded-xl bg-slate-900 px-[18px] py-3 text-[13px] font-semibold text-white shadow-[0_12px_30px_rgba(15,23,42,0.3)]">
          {message}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useScanToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useScanToast는 ScanToastProvider 안에서만 사용할 수 있습니다.");
  return ctx;
}
