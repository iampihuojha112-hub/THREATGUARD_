"use client";

import { Cell, Pie, PieChart, Tooltip } from "recharts";
import type { DashboardData } from "@/types";
import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export function PhishingPieChart({ data }: { data: DashboardData["phishing_vs_safe"] }) {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const colors = [CHART_COLORS.phishing, CHART_COLORS.safe];
  return (
    <div>
      <ChartFrame empty={total === 0} height={220}>
        {({ width, height }) => (
          <PieChart width={width} height={height}>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={62} outerRadius={90} paddingAngle={total > 0 && data.every((d) => d.value > 0) ? 3 : 0} stroke="none">
              {data.map((_, i) => (
                <Cell key={i} fill={colors[i]} />
              ))}
            </Pie>
            <Tooltip {...tooltipStyle} />
          </PieChart>
        )}
      </ChartFrame>
      <ul className="mt-2 flex justify-center gap-6 text-sm">
        {data.map((d, i) => (
          <li key={d.name} className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: colors[i] }} />
            <span className="text-muted-foreground">{d.name}</span>
            <span className="font-medium tabular-nums">{d.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
