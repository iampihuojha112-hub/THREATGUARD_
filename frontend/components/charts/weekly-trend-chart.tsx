"use client";

import { Area, AreaChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardData } from "@/types";
import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export function WeeklyTrendChart({ data }: { data: DashboardData["weekly_trend"] }) {
  const empty = data.every((d) => d.phishing + d.safe === 0);
  return (
    <ChartFrame empty={empty}>
      {({ width, height }) => (
        <AreaChart width={width} height={height} data={data} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="gPhish" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={CHART_COLORS.phishing} stopOpacity={0.45} />
              <stop offset="100%" stopColor={CHART_COLORS.phishing} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gSafe" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={CHART_COLORS.safe} stopOpacity={0.4} />
              <stop offset="100%" stopColor={CHART_COLORS.safe} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="week" stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke={CHART_COLORS.axis} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
          <Tooltip {...tooltipStyle} />
          <Legend iconType="circle" wrapperStyle={{ fontSize: 12, color: CHART_COLORS.axis }} />
          <Area type="monotone" dataKey="phishing" name="Threats" stroke={CHART_COLORS.phishing} strokeWidth={2} fill="url(#gPhish)" />
          <Area type="monotone" dataKey="safe" name="Safe" stroke={CHART_COLORS.safe} strokeWidth={2} fill="url(#gSafe)" />
        </AreaChart>
      )}
    </ChartFrame>
  );
}
