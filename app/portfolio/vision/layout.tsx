import LessonSidebar from "@/components/lesson-sidebar";

export default function VisionLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[calc(100dvh-var(--site-header-height))] w-full overflow-x-clip bg-[#fbfbfd]">
      <LessonSidebar />
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
