export interface EmailSendRequest {
  to: string;
  prompt: string;
}

export interface EmailSendResponse {
  to: string;
  subject: string;
  body: string;
  status: string;
}

export async function sendEmail(req: EmailSendRequest): Promise<EmailSendResponse> {
  const res = await fetch("/api/ontology/dispatch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task: "이메일 작성",
      payload: { to: req.to, prompt: req.prompt },
    }),
  });
  if (!res.ok) throw new Error(`전송 실패 (${res.status})`);
  const data = await res.json();
  return data.result as EmailSendResponse;
}
