"use client";

import { useEffect, useRef, useState } from "react";
import { fetchContacts, type ApiContact } from "@/lib/chef-address";
import { cn } from "@/lib/utils";

type Props = {
  value: string;
  onChange: (value: string) => void;
  onBlur: () => void;
  error?: boolean;
  placeholder?: string;
};

export default function EmailAutocomplete({ value, onChange, onBlur, error, placeholder }: Props) {
  const [contacts, setContacts] = useState<ApiContact[]>([]);
  const [open, setOpen] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchContacts().then(setContacts).catch(() => {});
  }, []);

  const suggestions =
    value.length >= 1
      ? contacts.filter((c) => {
          const q = value.toLowerCase();
          return c.email.toLowerCase().includes(q) || c.name.toLowerCase().includes(q);
        })
      : [];

  const select = (email: string) => {
    onChange(email);
    setOpen(false);
    setActiveIdx(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      select(suggestions[activeIdx].email);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  // 외부 클릭 시 닫기
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={containerRef} className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
          setActiveIdx(-1);
        }}
        onBlur={onBlur}
        onFocus={() => { if (value.length >= 1) setOpen(true); }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        className={cn(
          "w-full rounded-lg border bg-background px-3 py-2.5 text-sm outline-none",
          "placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/40",
          error ? "border-destructive" : "border-border"
        )}
      />

      {open && suggestions.length > 0 && (
        <ul className="absolute z-50 mt-1 w-full overflow-hidden rounded-xl border border-black/10 bg-white shadow-lg">
          {suggestions.map((c, i) => (
            <li key={c.email}>
              <button
                type="button"
                onMouseDown={() => select(c.email)}
                className={cn(
                  "flex w-full items-center gap-3 px-3 py-2.5 text-left transition",
                  i === activeIdx ? "bg-primary/5" : "hover:bg-[#f5f5f7]"
                )}
              >
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                  {c.name.charAt(0)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-[#1d1d1f]">{c.name}</p>
                  <p className="truncate text-xs text-muted-foreground">{c.email}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
