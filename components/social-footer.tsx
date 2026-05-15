"use client";

import { Github } from "lucide-react";

function XIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

export default function SocialFooter() {
  return (
    <div className="flex flex-col items-center gap-4 py-6">
      <div className="flex flex-wrap items-center justify-center gap-6">
        <a
          href="https://github.com/Whoareryu"
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-center gap-3 px-5 py-3 bg-card border border-border rounded-xl hover:border-primary/50 hover:bg-card/80 transition-all"
        >
          <Github className="w-5 h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground">GitHub</span>
            <span className="text-sm font-medium text-foreground">@Whoareryu</span>
          </div>
        </a>

        <a
          href="https://x.com/Who_are_ryu__"
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-center gap-3 px-5 py-3 bg-card border border-border rounded-xl hover:border-primary/50 hover:bg-card/80 transition-all"
        >
          <XIcon className="w-5 h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground">X (Twitter)</span>
            <span className="text-sm font-medium text-foreground">@Who_are_ryu__</span>
          </div>
        </a>
      </div>

      <div className="pointer-events-none inline-flex items-center justify-center rounded-xl border border-border bg-card px-5 py-3 text-sm text-muted-foreground select-none">
        문의사항 fbwns1234@gmail.com
      </div>
    </div>
  );
}
