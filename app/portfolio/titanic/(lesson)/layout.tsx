export default function LessonLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="px-4 pt-10 pb-12 md:px-8 md:pt-12 md:pb-14">
      {children}
    </main>
  );
}
