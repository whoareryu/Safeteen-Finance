"use client";

import { useState } from "react";
import Link from "next/link";
import { X, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogTitle } from "@/components/ui/dialog";

const COURSES = [
  {
    href: "/portfolio/titanic",
    title: "타이타닉",
    description: "타이타닉 데이터 분석·Gemini 채팅으로 이동합니다.",
  },
] as const;

export default function HimediaCoursePicker() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <div className="w-full max-w-md">
        <Button
          type="button"
          variant="ghost"
          onClick={() => setOpen(true)}
          className="neon-hit-shield btn-white h-auto w-full justify-between gap-3 rounded-2xl px-5 py-4 text-left hover:bg-transparent"
        >
          <span className="text-base font-semibold tracking-tight sm:text-lg">
            하이미디어 재직자 AI 과정
          </span>
          <ChevronRight
            className="h-5 w-5 shrink-0 text-muted-foreground"
            aria-hidden
          />
        </Button>
      </div>

      <DialogContent showCloseButton={false} className="modal-panel">
        <DialogClose asChild>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="btn-white absolute right-4 top-4 h-auto w-auto p-2"
            aria-label="닫기"
          >
            <X className="h-5 w-5" />
          </Button>
        </DialogClose>

        <DialogTitle className="mb-2 pr-10 text-center text-2xl font-bold">
          <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
            하이미디어 재직자 AI 과정
          </span>
        </DialogTitle>
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
      </DialogContent>
    </Dialog>
  );
}
