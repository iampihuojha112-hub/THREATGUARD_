"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/types";

const LEVEL_COLOR: Record<RiskLevel, string> = {
  low: "#10b981",
  medium: "#f59e0b",
  high: "#f97316",
  critical: "#f43f5e",
};

/** Semicircle gauge. The needle sweeps to the risk score on load. */
export function RiskGauge({ score, level, className }: { score: number; level: RiskLevel; className?: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const frame = requestAnimationFrame(() => setShown(clamped));
    return () => cancelAnimationFrame(frame);
  }, [clamped]);

  const radius = 90;
  const arcLength = Math.PI * radius;
  const color = LEVEL_COLOR[level];
  const angle = -90 + (shown / 100) * 180;

  return (
    <div className={cn("relative mx-auto w-full max-w-[300px]", className)} role="img" aria-label={`Risk score ${clamped.toFixed(0)} out of 100, ${level} risk`}>
      <svg viewBox="0 0 220 130" className="w-full overflow-visible">
        <path d="M 20 110 A 90 90 0 0 1 200 110" fill="none" stroke="hsl(228 35% 16%)" strokeWidth="14" strokeLinecap="round" />
        <path
          d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={arcLength}
          strokeDashoffset={arcLength * (1 - shown / 100)}
          style={{ transition: "stroke-dashoffset 900ms cubic-bezier(.2,.8,.2,1)" }}
        />
        <g style={{ transformOrigin: "110px 110px", transform: `rotate(${angle}deg)`, transition: "transform 900ms cubic-bezier(.2,.8,.2,1)" }}>
          <line x1="110" y1="110" x2="110" y2="34" stroke="hsl(220 30% 94%)" strokeWidth="3" strokeLinecap="round" />
        </g>
        <circle cx="110" cy="110" r="7" fill="hsl(220 30% 94%)" />
        <text x="22" y="128" fill="hsl(224 16% 63%)" fontSize="10" textAnchor="middle">0</text>
        <text x="198" y="128" fill="hsl(224 16% 63%)" fontSize="10" textAnchor="middle">100</text>
      </svg>
      <div className="-mt-2 text-center">
        <div className="text-5xl font-semibold tabular-nums" style={{ color }}>
          {clamped.toFixed(0)}
        </div>
        <div className="mt-1 text-sm capitalize text-muted-foreground">{level} risk</div>
      </div>
    </div>
  );
}
