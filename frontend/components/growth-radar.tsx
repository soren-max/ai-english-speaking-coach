"use client";

import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface RadarDataItem {
  dimension: string;
  [key: string]: number | string;
}

interface GrowthRadarProps {
  data: RadarDataItem[];
  colors: string[];
}

export default function GrowthRadar({ data, colors }: GrowthRadarProps) {
  // Extract session keys (everything except "dimension")
  const sessionKeys = data.length > 0
    ? Object.keys(data[0]).filter((k) => k !== "dimension")
    : [];

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadar data={data} cx="50%" cy="50%" outerRadius="65%">
          <PolarGrid stroke="hsl(var(--border))" gridType="polygon" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "hsl(var(--foreground))", fontSize: 12, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          {sessionKeys.map((key, i) => (
            <Radar
              key={key}
              name={key}
              dataKey={key}
              stroke={colors[i % colors.length]}
              fill={colors[i % colors.length]}
              fillOpacity={0.08}
              strokeWidth={2}
              dot={{ r: 3, fill: colors[i % colors.length] }}
            />
          ))}
          <Legend
            wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
            iconType="circle"
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
