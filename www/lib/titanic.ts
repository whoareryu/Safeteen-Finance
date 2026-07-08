export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export interface SmithChatResponse {
  reply: string;
}

export async function smithChat(messages: ChatMessage[]): Promise<string> {
  const res = await fetch("/api/titanic/smith/chat", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  const data = (await res.json().catch(() => ({}))) as {
    reply?: string;
    error?: string;
    detail?: unknown;
  };

  if (!res.ok) {
    throw new Error(data.error ?? `HTTP ${res.status}`);
  }

  return data.reply ?? "";
}
