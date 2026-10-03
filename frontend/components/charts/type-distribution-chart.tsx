"use client";

import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardData } from "@/types";
import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export function TypeDistributionChart({ data }: { data: DashboardData["type_distribution"] }) {
  const rows = data.map((d) => ({ name: d.name, threats: d.threats, safe: d.value - d.threats }));
  const empty = rows.every((d) => d.threats + d.safe === 0);
  return (
    <ChartFrame empty={empty} height={220}>
      {({ width, height }) => (
        <BarChart width={width} height={height} data={rows} layout="vertical" margin={{ top: 4, right: 16, left: 4, bottom: 0 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
          <YAxis type="category" dataKey="name" stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} width={48} />
          <Tooltip {...tooltipStyle} />
          <Legend iconType="circle" wrapperStyle={{ fontSize: 12, color: CHART_COLORS.axis }} />
          <Bar dataKey="threats" name="Threats" stackId="t" fill={CHART_COLORS.phishing} maxBarSize={26} />
          <Bar dataKey="safe" name="Safe" stackId="t" fill={CHART_COLORS.safe} maxBarSize={26} radius={[0, 4, 4, 0]} />
        </BarChart>
      )}
    </ChartFrame>
  );
}
