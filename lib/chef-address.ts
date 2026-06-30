export interface ApiContact {
  id: number;
  name: string;
  email: string;
  company: string;
  phone: string;
}

export async function fetchContacts(): Promise<ApiContact[]> {
  const res = await fetch("/api/chef/address/contacts");
  if (!res.ok) throw new Error(`연락처 조회 실패 (${res.status})`);
  return res.json() as Promise<ApiContact[]>;
}

export async function uploadContactsFile(file: File): Promise<{ saved: number }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/chef/address/upload", { method: "POST", body: form });
  if (!res.ok) throw new Error(`업로드 실패 (${res.status})`);
  return res.json() as Promise<{ saved: number }>;
}
