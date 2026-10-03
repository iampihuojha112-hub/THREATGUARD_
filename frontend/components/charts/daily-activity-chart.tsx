"use client";

import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardData } from "@/types";
import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export function DailyActivityChart({ data }: { data: DashboardData["daily_activity"] }) {
  const empty = data.every((d) => d.scans === 0);
  return (
    <ChartFrame empty={empty}>
      {({ width, height }) => (
        <BarChart width={width} height={height} data={data} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" stroke={CHART_COLORS.axis} fontSize={11} tickLine={false} axisLine={false} interval={width < 480 ? 2 : 0} />
          <YAxis stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
          <Tooltip {...tooltipStyle} />
          <Bar dataKey="scans" name="Scans" fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} maxBarSize={28} />
        </BarChart>
      )}
    </ChartFrame>
  );
}
