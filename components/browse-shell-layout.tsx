export default function BrowseShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="browse-shell min-h-[calc(100dvh-var(--site-header-height))] w-full">
      {children}
    </div>
  );
}
