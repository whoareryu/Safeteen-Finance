"use client";

import type { CSSProperties } from "react";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

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

const NEON_COLORS = [
  "rgba(0, 255, 255, 0.75)",
  "rgba(255, 0, 255, 0.68)",
  "rgba(192, 132, 252, 0.72)",
  "rgba(56, 232, 255, 0.7)",
  "rgba(251, 146, 232, 0.68)",
  "rgba(253, 224, 71, 0.55)",
];

function isNeonHiddenPath(pathname: string) {
  return (
    pathname === "/seoulmate" ||
    pathname === "/titanic" ||
    pathname.startsWith("/seoulmate/") ||
    pathname.startsWith("/titanic/")
  );
}

function generateLines(count: number): LineSpec[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `${Date.now()}-${i}-${Math.random().toString(36).slice(2, 9)}`,
    topPct: 6 + Math.random() * 88,
    widthVw: 20 + Math.random() * 38,
    heightPx: Math.random() > 0.65 ? 2 : 1,
    durationSec: 2.8 + Math.random() * 5,
    delaySec: Math.random() * 5,
    color: NEON_COLORS[i % NEON_COLORS.length]!,
    blurPx: 6 + Math.random() * 10,
    skewDeg: (Math.random() - 0.5) * 4,
  }));
}

export default function NeonFlowLines() {
  const pathname = usePathname();
  const [lines, setLines] = useState<LineSpec[]>([]);
  const [disabled, setDisabled] = useState(false);

  const hidden = isNeonHiddenPath(pathname);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mq.matches) {
      setDisabled(true);
      return;
    }
  }, []);

  useEffect(() => {
    if (disabled || hidden) {
      setLines([]);
      return;
    }
    setLines(generateLines(6));
  }, [disabled, hidden]);

  if (disabled || hidden || lines.length === 0) return null;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-[2] overflow-hidden"
      aria-hidden
    >
      {lines.flatMap((line) => {
        const baseStyle = {
          left: "50%",
          top: `${line.topPct}%`,
          width: `${line.widthVw}vw`,
          height: `${line.heightPx}px`,
          background: `linear-gradient(90deg, transparent 0%, ${line.color} 18%, ${line.color} 82%, transparent 100%)`,
          boxShadow: `0 0 ${line.blurPx}px ${line.blurPx * 0.45}px ${line.color}`,
          ["--neon-skew" as string]: `${line.skewDeg}deg`,
          ["--neon-opacity-mid" as string]: "0.5",
          animation: `neon-line-drift-h ${line.durationSec}s linear infinite`,
        } as CSSProperties;

        const delayA = -line.delaySec;
        const delayB = -(line.delaySec + line.durationSec / 2);

        return [
          <div
            key={`${line.id}-a`}
            className="absolute will-change-transform"
            style={{
              ...baseStyle,
              animationDelay: `${delayA}s`,
            }}
          />,
          <div
            key={`${line.id}-b`}
            className="absolute will-change-transform"
            style={{
              ...baseStyle,
              animationDelay: `${delayB}s`,
            }}
          />,
        ];
      })}
    </div>
  );
}
