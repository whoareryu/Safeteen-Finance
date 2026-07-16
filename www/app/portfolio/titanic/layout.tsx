import LessonMobileDrawer from "@/components/lesson-mobile-drawer";
import LessonSidebar from "@/components/lesson-sidebar";

export default function TitanicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[calc(100dvh-var(--site-header-height))] w-full overflow-x-clip bg-background">
      <LessonSidebar />
      <div className="min-w-0 flex-1">
        <div className="sticky top-[var(--site-header-height)] z-10 border-b border-border bg-background px-4 py-2 md:hidden">
          <LessonMobileDrawer />
        </div>
        {children}
      </div>
    </div>
  );
}
