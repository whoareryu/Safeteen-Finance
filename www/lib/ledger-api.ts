export interface ReceiptItem {
  name: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

export interface Receipt {
  id: number;
  owner_user_id: number;
  image_url: string;
  store_name: string;
  purchase_date: string;
  total_amount: number;
  category: string;
  items: ReceiptItem[];
  created_at: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  const data = (await res.json().catch(() => ({}))) as T & { detail?: unknown };
  if (!res.ok) {
    const detail = typeof data?.detail === "string" ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

export async function listReceipts(): Promise<Receipt[]> {
  const res = await fetch("/api/ledger/receipts", { cache: "no-store" });
  return parseOrThrow<Receipt[]>(res);
}

export async function fetchReceipt(id: number): Promise<Receipt> {
  const res = await fetch(`/api/ledger/receipts/${id}`, { cache: "no-store" });
  return parseOrThrow<Receipt>(res);
}
