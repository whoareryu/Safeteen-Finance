import ScanAppShell from "@/components/scan-app-shell";
import { ScanResultProvider } from "@/components/scan-result-context";
import { ScanToastProvider } from "@/components/scan-toast";

export default function ScanLayout({ children }: { children: React.ReactNode }) {
  return (
    <ScanResultProvider>
      <ScanToastProvider>
        <ScanAppShell>{children}</ScanAppShell>
      </ScanToastProvider>
    </ScanResultProvider>
  );
}
