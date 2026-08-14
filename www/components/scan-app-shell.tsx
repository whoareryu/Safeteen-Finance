"use client";

import { useState } from "react";
import { ScanSidebarDesktop, ScanSidebarMobile } from "@/components/scan-sidebar";
import ScanHeader from "@/components/scan-header";

/** SafeTeen 앱 전체(홈 포함)가 공유하는 좌측 사이드바 + 상단 서브헤더 셸. */
export default function ScanAppShell({
  children,
  maxWidthClassName = "max-w-4xl",
}: {
  children: React.ReactNode;
  maxWidthClassName?: string;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-[calc(100dvh-var(--site-header-height))] bg-slate-50 md:pl-56">
      <ScanSidebarDesktop />
      <ScanSidebarMobile open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <ScanHeader onMenuClick={() => setSidebarOpen(true)} />

      <main className={`mx-auto ${maxWidthClassName} px-4 py-6 sm:px-6 sm:py-8`}>{children}</main>
    </div>
  );
}
