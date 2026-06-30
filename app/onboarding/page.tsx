import OnboardingWizard from "@/components/onboarding-wizard";

export default function OnboardingPage({
  searchParams,
}: {
  searchParams: Record<string, string | string[] | undefined>;
}) {
  const editMode = searchParams.edit === "1";
  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))]">
      <OnboardingWizard editMode={editMode} />
    </main>
  );
}
