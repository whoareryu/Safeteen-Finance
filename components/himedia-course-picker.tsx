"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X, ChevronRight } from "lucide-react";

const COURSES = [
  {
    href: "/seoulmate",
    title: "SeoulMate",
    description: "서울 메이트 AI 과정으로 이동합니다.",
  },
  {
    href: "/titanic",
    title: "타이타닉",
    description: "타이타닉 프로젝트 과정으로 이동합니다.",
  },
] as const;

export default function HimediaCoursePicker() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  const close = () => setOpen(false);

  return (
    <>
      <div className="w-full max-w-md">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="neon-hit-shield btn-white flex w-full items-center justify-between gap-3 rounded-2xl px-5 py-4 text-left"
        >
          <span className="text-base font-semibold tracking-tight sm:text-lg">
            하이미디어 재직자 AI 과정
          </span>
          <ChevronRight
            className="h-5 w-5 shrink-0 text-muted-foreground"
            aria-hidden
          />
        </button>
      </div>

      {open ? (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div className="modal-overlay absolute inset-0" onClick={close} aria-hidden />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="himedia-modal-title"
            className="modal-panel"
          >
            <button
              type="button"
              onClick={close}
              className="btn-white absolute right-4 top-4 p-2"
              aria-label="닫기"
            >
              <X className="h-5 w-5" />
            </button>

            <h2
              id="himedia-modal-title"
              className="mb-2 pr-10 text-center text-2xl font-bold"
            >
              <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
                하이미디어 재직자 AI 과정
              </span>
            </h2>
            <p className="mb-6 text-center text-sm text-muted-foreground">
              참여할 과정을 선택해 주세요.
            </p>

            <div className="modal-divider mb-5" />

            <div className="flex flex-col gap-3" role="list">
              {COURSES.map((course) => (
                <Link
                  key={course.href}
                  href={course.href}
                  onClick={close}
                  role="listitem"
                  className="modal-option group"
                >
                  <div className="min-w-0 text-left">
                    <p className="text-base font-semibold text-foreground group-hover:text-primary">
                      {course.title}
                    </p>
                    <p className="mt-0.5 text-sm text-muted-foreground">
                      {course.description}
                    </p>
                  </div>
                  <ChevronRight className="h-5 w-5 shrink-0 text-muted-foreground transition-colors group-hover:text-primary" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
