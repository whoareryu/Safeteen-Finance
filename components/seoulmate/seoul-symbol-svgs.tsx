import type { SVGProps } from "react";
import { cn } from "@/lib/utils";

export function SeoulNamsanIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 48 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0 text-primary", className)}
      aria-hidden
      {...props}
    >
      <path
        d="M24 4 L28 20 L32 22 L32 60 L16 60 L16 22 L20 20 Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="currentColor"
        fillOpacity="0.15"
      />
      <circle cx="24" cy="12" r="4" fill="currentColor" fillOpacity="0.35" />
      <path d="M12 60 H36" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

/** 한옥 지붕 곡선 */
export function SeoulHanokIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 64 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0 text-primary", className)}
      aria-hidden
      {...props}
    >
      <path
        d="M4 28 Q32 4 60 28 L60 36 H4 Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="currentColor"
        fillOpacity="0.12"
      />
      <path d="M20 28 V36 M44 28 V36" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** 궁궐 정문 느낌의 단순 실루엣 */
export function SeoulPalaceIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 56 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0 text-primary", className)}
      aria-hidden
      {...props}
    >
      <path
        d="M4 20 L28 8 L52 20 V44 H4 Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="currentColor"
        fillOpacity="0.1"
      />
      <rect x="22" y="26" width="12" height="18" stroke="currentColor" strokeWidth="1.5" fill="none" />
    </svg>
  );
}

/** 한강·다리 실루엣 */
export function SeoulRiverIcon({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 64 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0 text-primary", className)}
      aria-hidden
      {...props}
    >
      <path
        d="M0 24 Q16 18 32 22 T64 20"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
      />
      <path d="M8 26 H56 L52 34 H12 Z" fill="currentColor" fillOpacity="0.2" />
    </svg>
  );
}
