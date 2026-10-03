"use client";

import type { ReactNode } from "react";
import { useElementWidth } from "@/hooks/use-element-size";

interface ChartFrameProps {
  height?: number;
  empty?: boolean;
  emptyMessage?: string;
  children: (size: { width: number; height: number }) => ReactNode;
}

/** Gives charts explicit pixel dimensions measured from the parent (no ResponsiveContainer). */
export function ChartFrame({ height = 260, empty, emptyMessage = "No data yet. Analyze an email to see activity here.", children }: ChartFrameProps) {
  const { ref, width } = useElementWidth<HTMLDivElement>();

  return (
    <div ref={ref} style={{ width: "100%", height }} className="relative">
      {empty ? (
        <div className="flex h-full items-center justify-center px-6 text-center text-sm text-muted-foreground">{emptyMessage}</div>
      ) : (
        width > 0 && children({ width, height })
      )}
    </div>
  );
}

export const CHART_COLORS = {
  phishing: "#f43f5e",
  safe: "#10b981",
  primary: "#8b5cf6",
  blue: "#3b82f6",
  grid: "#1e2749",
  axis: "#8b93b8",
};

export const tooltipStyle = {
  contentStyle: {
    background: "#0b1030",
    border: "1px solid #232d5a",
    borderRadius: 8,
    fontSize: 12,
    color: "#e6e9f5",
  },
  labelStyle: { color: "#aab2d5" },
  itemStyle: { color: "#e6e9f5" },
  cursor: { fill: "rgba(139,92,246,0.08)" },
};
