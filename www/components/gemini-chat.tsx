"use client";

import {
  Camera,
  Mic,
  Plus,
  SendHorizontal,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

type Role = "user" | "assistant";

type Msg = { id: string; role: Role; content: string };

type AttachedImage = { file: File; previewUrl: string };

const DEFAULT_MODEL = "exaone3.5:2.4b";

function id() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

type GeminiChatProps = {
  variant?: "dark" | "apple";
  /** 기본 `/api/chat` — 타이타닉은 `/api/titanic/chat` */
  apiPath?: string;
  inputPlaceholder?: string;
  /** 기본 exaone3.5:2.4b */
  model?: string;
  /** 제공 시에만 첨부(+)/카메라 버튼이 활성화됨. 선택한 이미지를 받아 채팅창에 표시할 텍스트를 반환 */
  onImageAttach?: (file: File) => Promise<string>;
};

export default function GeminiChat({
  variant = "dark",
  apiPath = "/api/chat",
  inputPlaceholder = "무엇이든 물어보세요",
  model = DEFAULT_MODEL,
  onImageAttach,
}: GeminiChatProps) {
  const isApple = variant === "apple";
  const neonShield = isApple ? "neon-hit-shield" : "";
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachedImage, setAttachedImage] = useState<AttachedImage | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0);
  const listRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const scrollBottom = useCallback(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  useEffect(() => {
    scrollBottom();
  }, [messages, loading, scrollBottom]);

  const askChat = useCallback(
    async (historyBase: { role: Role; content: string }[], text: string) => {
      const history = [...historyBase, { role: "user" as const, content: text }];
      const res = await fetch(apiPath, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history, model }),
      });
      const data = (await res.json()) as {
        text?: string;
        model?: string;
        error?: boolean | string;
        message?: string;
        detail?: string | unknown;
      };

      if (!res.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
              ? "요청 형식이 올바르지 않습니다."
              : null;
        const msg =
          detail ??
          (typeof data.message === "string"
            ? data.message
            : typeof data.error === "string"
              ? data.error
              : res.status === 502
                ? "백엔드 또는 AI 모델 연결에 실패했습니다. backend 서버를 확인하세요."
                : "요청에 실패했습니다.");
        throw new Error(msg);
      }
      if (!data.text) {
        throw new Error("응답이 비어 있습니다.");
      }
      return data.text;
    },
    [apiPath, model]
  );

  const removeAttachedImage = useCallback(() => {
    setAttachedImage((prev) => {
      if (prev) URL.revokeObjectURL(prev.previewUrl);
      return null;
    });
  }, []);

  const send = useCallback(async () => {
    const text = input.trim();
    const image = attachedImage;
    if ((!text && !image) || loading) return;

    setError(null);
    setInput("");
    setAttachedImage(null);
    setLoading(true);

    const userLabel = image
      ? text
        ? `📷 ${image.file.name}\n${text}`
        : `📷 ${image.file.name}`
      : text;
    setMessages((prev) => [...prev, { id: id(), role: "user", content: userLabel }]);

    const historyBase = messages.map((m) => ({ role: m.role, content: m.content }));

    try {
      let diagnosisText: string | null = null;
      if (image && onImageAttach) {
        diagnosisText = await onImageAttach(image.file);
        if (!text) {
          // 사진만 보낸 경우: 진단 결과를 그대로 답변으로 보여준다
          setMessages((prev) => [...prev, { id: id(), role: "assistant", content: diagnosisText! }]);
          return;
        }
      }

      const askText = diagnosisText ? `${diagnosisText}\n\n${text}` : text;
      const replyText = await askChat(historyBase, askText);
      setMessages((prev) => [...prev, { id: id(), role: "assistant", content: replyText }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "요청에 실패했습니다.");
    } finally {
      setLoading(false);
      if (image) URL.revokeObjectURL(image.previewUrl);
    }
  }, [askChat, attachedImage, input, loading, messages, onImageAttach]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const handleImagePicked = useCallback((file: File | null) => {
    if (!file) return;
    setError(null);
    setAttachedImage((prev) => {
      if (prev) URL.revokeObjectURL(prev.previewUrl);
      return { file, previewUrl: URL.createObjectURL(file) };
    });
  }, []);

  const onDragEnter = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      if (!onImageAttach) return;
      e.preventDefault();
      dragCounter.current += 1;
      setIsDragging(true);
    },
    [onImageAttach]
  );

  const onDragOver = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      if (!onImageAttach) return;
      e.preventDefault();
    },
    [onImageAttach]
  );

  const onDragLeave = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      if (!onImageAttach) return;
      e.preventDefault();
      dragCounter.current -= 1;
      if (dragCounter.current <= 0) {
        dragCounter.current = 0;
        setIsDragging(false);
      }
    },
    [onImageAttach]
  );

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      if (!onImageAttach) return;
      e.preventDefault();
      dragCounter.current = 0;
      setIsDragging(false);
      const file = Array.from(e.dataTransfer.files).find((f) => f.type.startsWith("image/"));
      if (!file) {
        setError("이미지 파일만 첨부할 수 있습니다.");
        return;
      }
      handleImagePicked(file);
    },
    [onImageAttach, handleImagePicked]
  );

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "0px";
    ta.style.height = `${Math.min(Math.max(ta.scrollHeight, 26), 120)}px`;
  }, [input]);

  const hasThread = messages.length > 0 || loading;
  const canSend = (input.trim().length > 0 || !!attachedImage) && !loading;

  const iconBtn = isApple
    ? "rounded-full p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
    : "rounded-full p-2 text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]";

  const toolBtn = isApple
    ? "flex items-center gap-1.5 rounded-full border border-border bg-card px-2.5 py-1.5 text-sm text-foreground shadow-sm transition-colors hover:bg-secondary"
    : "flex items-center gap-1.5 rounded-full px-2 py-1.5 text-sm text-[#c4c7c5] transition-colors hover:bg-white/10 hover:text-[#e8eaed]";

  return (
    <div
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className="mx-auto w-full max-w-xl"
    >
      <div
        className={cn(
          "gemini-chat-shell relative flex min-h-[136px] w-full min-w-0 flex-col rounded-[28px] px-4 pb-2.5 pt-3 md:min-h-[152px]",
          neonShield,
          isApple
            ? "border border-border bg-card text-foreground shadow-sm"
            : "border border-white/[0.12] bg-[#1e1f20] text-[#e3e3e3] shadow-xl",
          isDragging && (isApple ? "border-primary ring-2 ring-primary/40" : "border-[#8ab4f8] ring-2 ring-[#8ab4f8]/40")
        )}
      >
        {isDragging && (
          <div
            className={cn(
              "pointer-events-none absolute inset-0 z-10 flex items-center justify-center rounded-[28px] text-sm font-medium",
              isApple ? "bg-primary/10 text-primary" : "bg-[#8ab4f8]/10 text-[#8ab4f8]"
            )}
          >
            여기에 사진을 놓아 첨부하세요
          </div>
        )}

        {attachedImage && (
          <div className="relative mb-4 mt-1 inline-block w-fit">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={attachedImage.previewUrl}
              alt="첨부한 사진 미리보기"
              className="h-32 w-32 rounded-2xl object-cover"
            />
            <button
              type="button"
              onClick={removeAttachedImage}
              aria-label="첨부 사진 삭제"
              title="첨부 사진 삭제"
              className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-foreground/80 text-background shadow-md transition hover:bg-foreground"
            >
              <X className="size-3.5" strokeWidth={2.5} />
            </button>
            <span
              className={cn(
                "absolute -bottom-2 left-2 max-w-[85%] truncate rounded-full border px-2.5 py-1 text-[11px] shadow-sm",
                isApple
                  ? "border-border bg-card text-foreground"
                  : "border-white/[0.12] bg-[#1e1f20] text-[#e3e3e3]"
              )}
            >
              {attachedImage.file.name}
            </span>
          </div>
        )}

        <div className="flex min-h-[84px] flex-1 flex-col justify-center py-1">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={inputPlaceholder}
            disabled={loading}
            className={cn(
              "w-full max-h-[120px] min-h-[26px] resize-none overflow-y-auto bg-transparent text-left text-[15px] leading-relaxed outline-none disabled:opacity-60",
              isApple
                ? "text-foreground placeholder:text-muted-foreground"
                : "text-[#f1f3f4] placeholder:text-[#9aa0a6]"
            )}
          />
        </div>

        {error && (
          <p
            className={cn(
              "mb-1 shrink-0 text-xs",
              isApple ? "text-red-600" : "text-red-400"
            )}
            role="alert"
          >
            {error}
          </p>
        )}

        <div
          className={cn(
            "mt-0.5 flex shrink-0 flex-wrap items-center justify-between gap-x-2 gap-y-2 border-t pt-2.5",
            isApple ? "border-border" : "border-white/[0.08]"
          )}
        >
          <div className="flex items-center gap-0.5">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                void handleImagePicked(e.target.files?.[0] ?? null);
                e.target.value = "";
              }}
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(e) => {
                void handleImagePicked(e.target.files?.[0] ?? null);
                e.target.value = "";
              }}
            />
            <button
              type="button"
              className={iconBtn}
              aria-label={onImageAttach ? "사진 첨부" : "첨부 (준비 중)"}
              title={onImageAttach ? "사진 첨부" : "준비 중"}
              disabled={!onImageAttach || loading}
              onClick={() => fileInputRef.current?.click()}
            >
              <Plus className="size-5" strokeWidth={1.75} />
            </button>
            {onImageAttach && (
              <button
                type="button"
                className={iconBtn}
                aria-label="카메라로 촬영"
                title="카메라로 촬영"
                disabled={loading}
                onClick={() => cameraInputRef.current?.click()}
              >
                <Camera className="size-5" strokeWidth={1.75} />
              </button>
            )}
            <button
              type="button"
              className={toolBtn}
              aria-label="도구 (준비 중)"
              title="준비 중"
            >
              <SlidersHorizontal className="size-4" strokeWidth={1.75} />
              <span className="hidden sm:inline">도구</span>
            </button>
          </div>

          <div className="flex items-center gap-0.5">
            <button
              type="button"
              className={cn(iconBtn, !isApple && "opacity-60")}
              aria-label="음성 입력 (미지원)"
              title="미지원"
              disabled
            >
              <Mic className="size-5" strokeWidth={1.75} />
            </button>

            <button
              type="button"
              onClick={() => void send()}
              disabled={!canSend}
              className={cn(
                "rounded-full p-2 transition-colors disabled:cursor-not-allowed",
                isApple
                  ? canSend
                    ? "bg-primary text-primary-foreground hover:opacity-90"
                    : "text-muted-foreground/50"
                  : canSend
                    ? "bg-[#8ab4f8] text-[#1e1f20] hover:bg-[#a8c7fa]"
                    : "text-[#5f6368] opacity-60"
              )}
              aria-label="전송"
              title="전송"
            >
              <SendHorizontal className="size-5" strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </div>

      {hasThread && (
        <div
          ref={listRef}
          className={cn(
            "mt-3 max-h-[min(40vh,220px)] space-y-2 overflow-y-auto rounded-2xl border px-3 py-2 text-left text-sm",
            neonShield,
            isApple
              ? "border-border bg-card shadow-sm"
              : "border-border/40 bg-card/30"
          )}
        >
          {messages.map((m) => (
            <div
              key={m.id}
              className={cn(
                "rounded-xl px-2.5 py-1.5",
                m.role === "user"
                  ? isApple
                    ? "ml-6 rounded-br-sm border border-border bg-card text-foreground"
                    : "ml-6 rounded-br-sm bg-primary/15 text-foreground"
                  : isApple
                    ? "mr-4 rounded-bl-sm bg-secondary text-foreground"
                    : "mr-4 rounded-bl-sm bg-muted/40 text-foreground/90"
              )}
            >
              <p className="whitespace-pre-wrap break-words">{m.content}</p>
            </div>
          ))}
          {loading && (
            <div
              className={cn(
                "mr-4 rounded-xl rounded-bl-sm px-2.5 py-1.5",
                isApple
                  ? "bg-secondary text-muted-foreground"
                  : "bg-muted/40 text-muted-foreground"
              )}
            >
              답변 작성 중…
            </div>
          )}
        </div>
      )}

      <p
        className={cn(
          "mx-auto mt-2.5 max-w-xl px-2 text-center text-[11px] leading-snug sm:text-xs",
          isApple && "neon-text-shield",
          isApple ? "text-muted-foreground" : "text-[#8e918f]"
        )}
      >
        AI는 인물 등에 관한 정보 제공 시 실수를 할 수 있습니다.
      </p>
    </div>
  );
}
