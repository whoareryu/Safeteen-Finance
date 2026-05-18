"use client";

import type { CSSProperties } from "react";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

type LineSpec = {
  id: string;
  topPct: number;
  widthVw: number;
  heightPx: number;
  durationSec: number;
  delaySec: number;
  color: string;
  blurPx: number;
  skewDeg: number;
};

/** 흰 배경에서도 보이도록 채도·불투명도 높임 */
const NEON_COLORS = [
  "rgba(0, 195, 255, 0.92)",
  "rgba(220, 50, 255, 0.88)",
  "rgba(130, 70, 255, 0.9)",
  "rgba(0, 210, 200, 0.88)",
  "rgba(255, 80, 200, 0.86)",
  "rgba(255, 180, 0, 0.82)",
];

type NeonFlowLinesProps = {
  /** 메인 페이지 main 안에 넣을 때 */
  embedded?: boolean;
};

function isNeonHomePath(pathname: string) {
  return pathname === "/";
}

function generateLines(count: number): LineSpec[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `${Date.now()}-${i}-${Math.random().toString(36).slice(2, 9)}`,
    topPct: 8 + Math.random() * 84,
    widthVw: 22 + Math.random() * 36,
    heightPx: 2,
    durationSec: 2.8 + Math.random() * 5,
    delaySec: Math.random() * 5,
    color: NEON_COLORS[i % NEON_COLORS.length]!,
    blurPx: 4 + Math.random() * 5,
    skewDeg: (Math.random() - 0.5) * 4,
  }));
}

export default function NeonFlowLines({ embedded = false }: NeonFlowLinesProps) {
  const pathname = usePathname();
  const [lines, setLines] = useState<LineSpec[]>([]);
  const [reducedMotion, setReducedMotion] = useState(false);

  const hidden = embedded ? false : !isNeonHomePath(pathname);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (hidden) {
      setLines([]);
      return;
    }
    setLines(generateLines(8));
  }, [hidden]);

  if (hidden || lines.length === 0) return null;

  return (
    <div
      className={cn(
        "pointer-events-none overflow-hidden",
        embedded
          ? "absolute inset-0 z-[1]"
          : "fixed inset-0 z-[8]"
      )}
      aria-hidden
    >
      {lines.flatMap((line) => {
        const baseStyle = {
          left: "50%",
          top: `${line.topPct}%`,
          width: `${line.widthVw}vw`,
          height: `${line.heightPx}px`,
          background: `linear-gradient(90deg, transparent 0%, ${line.color} 15%, ${line.color} 85%, transparent 100%)`,
          boxShadow: `0 0 ${line.blurPx}px ${line.blurPx * 0.55}px ${line.color}, 0 0 ${line.blurPx * 1.4}px ${line.blurPx * 0.3}px ${line.color}`,
          ["--neon-skew" as string]: `${line.skewDeg}deg`,
          ["--neon-opacity-mid" as string]: "0.82",
          animation: reducedMotion
            ? undefined
            : `neon-line-drift-h ${line.durationSec}s linear infinite`,
          opacity: reducedMotion ? 0.75 : undefined,
        } as CSSProperties;

        const delayA = -line.delaySec;
        const delayB = -(line.delaySec + line.durationSec / 2);

        return [
          <div
            key={`${line.id}-a`}
            className="absolute will-change-transform"
            style={{
              ...baseStyle,
              animationDelay: reducedMotion ? undefined : `${delayA}s`,
            }}
          />,
          <div
            key={`${line.id}-b`}
            className="absolute will-change-transform"
            style={{
              ...baseStyle,
              animationDelay: reducedMotion ? undefined : `${delayB}s`,
            }}
          />,
        ];
      })}
    </div>
  );
}
