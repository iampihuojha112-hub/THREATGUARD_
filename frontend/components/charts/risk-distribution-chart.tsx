"use client";

import { Bar, BarChart, CartesianGrid, Cell, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardData } from "@/types";
import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

const BUCKET_COLORS = ["#10b981", "#84cc16", "#f59e0b", "#f97316", "#f43f5e"];

export function RiskDistributionChart({ data }: { data: DashboardData["risk_distribution"] }) {
  const empty = data.every((d) => d.count === 0);
  return (
    <ChartFrame empty={empty}>
      {({ width, height }) => (
        <BarChart width={width} height={height} data={data} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="range" stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
          <Tooltip {...tooltipStyle} />
          <Bar dataKey="count" name="Emails" radius={[4, 4, 0, 0]} maxBarSize={48}>
            {data.map((_, i) => (
              <Cell key={i} fill={BUCKET_COLORS[i]} />
            ))}
          </Bar>
        </BarChart>
      )}
    </ChartFrame>
  );
}
