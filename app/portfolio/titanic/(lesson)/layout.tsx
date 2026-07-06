import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getBackendBaseUrl } from "@/lib/backend-proxy";

async function isOwnerRequest(): Promise<boolean> {
  const base = getBackendBaseUrl();
  if (!base) return false;
  const ownerSession = (await cookies()).get("wr_owner_session")?.value;
  if (!ownerSession) return false;

  try {
    const res = await fetch(`${base}/auth/owner-check`, {
      headers: { Cookie: `wr_owner_session=${ownerSession}` },
      cache: "no-store",
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { is_owner: boolean };
    return data.is_owner;
  } catch {
    return false;
  }
}

export default async function LessonLayout({ children }: { children: React.ReactNode }) {
  if (!(await isOwnerRequest())) {
    redirect("/portfolio/titanic");
  }

  return (
    <main className="px-4 pt-10 pb-12 md:px-8 md:pt-12 md:pb-14">
      {children}
    </main>
  );
}
