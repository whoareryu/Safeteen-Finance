import OnboardingWizard from "@/components/onboarding-wizard";

export default function OnboardingPage() {
  return (
    <main className="min-h-[calc(100dvh-var(--site-header-height))]">
      <OnboardingWizard />
    </main>
  );
}
