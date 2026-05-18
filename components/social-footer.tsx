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
          className="surface-white group flex items-center gap-3 px-5 py-3"
        >
          <Github className="w-5 h-5 text-neutral-500 transition-colors group-hover:text-neutral-800" />
          <div className="flex flex-col">
            <span className="text-xs text-neutral-500">GitHub</span>
            <span className="text-sm font-medium text-neutral-800">@Whoareryu</span>
          </div>
        </a>

        <a
          href="https://x.com/Who_are_ryu__"
          target="_blank"
          rel="noopener noreferrer"
          className="surface-white group flex items-center gap-3 px-5 py-3"
        >
          <XIcon className="w-5 h-5 text-neutral-500 transition-colors group-hover:text-neutral-800" />
          <div className="flex flex-col">
            <span className="text-xs text-neutral-500">X (Twitter)</span>
            <span className="text-sm font-medium text-neutral-800">@Who_are_ryu__</span>
          </div>
        </a>
      </div>

      <div className="pointer-events-none inline-flex items-center justify-center rounded-xl border border-neutral-300 bg-neutral-50 px-5 py-3 text-sm text-neutral-600 shadow-sm select-none">
        문의사항 fbwns1234@gmail.com
      </div>
    </div>
  );
}
