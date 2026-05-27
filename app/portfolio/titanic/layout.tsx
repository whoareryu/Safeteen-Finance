import LessonSidebar from "@/components/lesson-sidebar";

export default function TitanicLessonLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-[calc(100dvh-var(--site-header-height))] w-full overflow-x-clip bg-[#fbfbfd]">
      <LessonSidebar />
      <main className="min-w-0 flex-1 px-4 pt-10 pb-12 md:px-8 md:pt-12 md:pb-14">
        {children}
      </main>
    </div>
  );
}

