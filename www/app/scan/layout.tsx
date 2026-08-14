"use client";

import { useState } from "react";
import { ScanSidebarDesktop, ScanSidebarMobile } from "@/components/scan-sidebar";
import ScanHeader from "@/components/scan-header";
import { ScanResultProvider } from "@/components/scan-result-context";

export default function ScanLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ScanResultProvider>
      <div className="min-h-[calc(100dvh-var(--site-header-height))] bg-slate-50 md:pl-56">
        <ScanSidebarDesktop />
        <ScanSidebarMobile open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <ScanHeader onMenuClick={() => setSidebarOpen(true)} />

        <main className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
      </div>
    </ScanResultProvider>
  );
}
