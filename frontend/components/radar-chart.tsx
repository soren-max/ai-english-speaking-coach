"use client";

import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarDataItem {
  dimension: string;
  score: number;
  fullMark: number;
}

interface RadarChartProps {
  data: Omit<RadarDataItem, "fullMark">[];
}

const COLORS: Record<string, string> = {
  Fluency: "hsl(142, 76%, 36%)",
  Grammar: "hsl(217, 91%, 60%)",
  Vocabulary: "hsl(271, 81%, 56%)",
  Communication: "hsl(24, 95%, 53%)",
};

export default function RadarChart({ data }: RadarChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    fullMark: 100,
  }));

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadar data={chartData} cx="50%" cy="50%" outerRadius="72%">
          <PolarGrid stroke="hsl(var(--border))" gridType="polygon" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "hsl(var(--foreground))", fontSize: 11, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            domain={[0, 100]}
            tick={false}
            axisLine={false}
            tickCount={5}
          />
          <Tooltip
            formatter={(value: number, name: string) => [`${value}/100`, name]}
            contentStyle={{
              background: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              fontSize: "13px",
            }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.15}
            strokeWidth={2.5}
            dot={{ r: 4, fill: "hsl(var(--primary))", strokeWidth: 2 }}
            activeDot={{ r: 6, strokeWidth: 0 }}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}

export { COLORS };
export type { RadarDataItem };
