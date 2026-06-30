export type Contact = {
  id: string;
  name: string;
  email: string;
  company?: string;
};

const KEY = "address_book_v1";

export function loadContacts(): Contact[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as Contact[];
  } catch {
    return [];
  }
}

export function saveContacts(contacts: Contact[]): void {
  localStorage.setItem(KEY, JSON.stringify(contacts));
}

export function addContacts(incoming: Omit<Contact, "id">[]): Contact[] {
  const existing = loadContacts();
  const existingEmails = new Set(existing.map((c) => c.email.toLowerCase()));
  const newOnes: Contact[] = incoming
    .filter((c) => !existingEmails.has(c.email.toLowerCase()))
    .map((c) => ({ ...c, id: crypto.randomUUID() }));
  const merged = [...existing, ...newOnes];
  saveContacts(merged);
  return merged;
}

export function deleteContact(id: string): Contact[] {
  const updated = loadContacts().filter((c) => c.id !== id);
  saveContacts(updated);
  return updated;
}

/** CSV 한 줄을 셀 배열로 분리 (따옴표 포함 처리) */
function splitCsvLine(line: string): string[] {
  const cells: string[] = [];
  let cur = "";
  let inQ = false;
  for (const ch of line) {
    if (ch === '"') { inQ = !inQ; continue; }
    if (ch === "," && !inQ) { cells.push(cur.trim()); cur = ""; }
    else cur += ch;
  }
  cells.push(cur.trim());
  return cells;
}

/**
 * CSV 텍스트 → Contact 배열
 * 지원 형식:
 *  - 커스텀: name/이름, email/이메일, company/회사
 *  - Google 연락처 내보내기: First Name, Last Name, E-mail 1 - Value, Organization Name
 */
export function parseCsvContacts(text: string): Omit<Contact, "id">[] {
  const lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const rawHeader = (lines[0] ?? "").split(",").map((s) => s.trim());
  const header = rawHeader.map((s) => s.toLowerCase());

  const find = (...candidates: string[]) =>
    header.findIndex((h) => candidates.some((c) => h === c || h.startsWith(c)));

  // 커스텀 단순 형식
  const iName    = find("name", "이름", "성명");
  const iEmail   = find("email", "이메일");
  const iCompany = find("company", "회사");

  // Google 연락처 형식
  const iFirst   = find("first name");
  const iLast    = find("last name");
  const iGEmail  = header.findIndex((h) => h.startsWith("e-mail") && h.includes("value"));
  const iGOrg    = find("organization name");

  const isGoogle = iFirst >= 0 && iGEmail >= 0;
  const isCustom = iName >= 0 && iEmail >= 0;

  if (!isGoogle && !isCustom) {
    throw new Error(
      "인식할 수 없는 CSV 형식입니다.\n" +
      "• 커스텀: name(이름), email(이메일) 컬럼\n" +
      "• Google 연락처 내보내기 파일 그대로 사용 가능"
    );
  }

  const contacts: Omit<Contact, "id">[] = [];
  for (const raw of lines.slice(1)) {
    const line = raw.trim();
    if (!line) continue;
    const cells = splitCsvLine(line);

    let name = "";
    let email = "";
    let company: string | undefined;

    if (isGoogle) {
      const first = cells[iFirst] ?? "";
      const last  = iLast >= 0 ? (cells[iLast] ?? "") : "";
      name    = [first, last].filter(Boolean).join(" ");
      email   = cells[iGEmail] ?? "";
      company = iGOrg >= 0 ? cells[iGOrg] || undefined : undefined;
    } else {
      name    = cells[iName] ?? "";
      email   = cells[iEmail] ?? "";
      company = iCompany >= 0 ? cells[iCompany] || undefined : undefined;
    }

    if (!name || !email || !email.includes("@")) continue;
    contacts.push({ name, email, company });
  }
  return contacts;
}
