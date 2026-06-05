"use client";

/** EmotionMeter — shows tension/confidence level with表情和颜色 */
import { AlertCircle, CheckCircle, MinusCircle } from "lucide-react";

interface EmotionMeterProps {
  tensionScore: number;   // 0-100
  confidenceLevel: "low" | "medium" | "high";
  size?: "sm" | "md";
}

export default function EmotionMeter({ tensionScore, confidenceLevel, size = "sm" }: EmotionMeterProps) {
  const isHigh = tensionScore >= 65;
  const isMid = tensionScore >= 35;

  const color = isHigh ? "text-red-500" : isMid ? "text-amber-500" : "text-green-500";
  const bgColor = isHigh ? "bg-red-50 dark:bg-red-950/30" : isMid ? "bg-amber-50 dark:bg-amber-950/30" : "bg-green-50 dark:bg-green-950/30";
  const borderColor = isHigh ? "border-red-200 dark:border-red-900" : isMid ? "border-amber-200 dark:border-amber-900" : "border-green-200 dark:border-green-900";
  const Icon = isHigh ? AlertCircle : isMid ? MinusCircle : CheckCircle;

  if (size === "sm") {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${color} ${bgColor}`}>
        <Icon className="w-3 h-3" />
        {confidenceLevel === "high" ? "Calm" : confidenceLevel === "medium" ? "Neutral" : "Tense"}
      </div>
    );
  }

  return (
    <div className={`border rounded-lg p-3 ${borderColor} ${bgColor}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-muted-foreground">Emotion</span>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${color}`}>{tensionScore}</span>
        <span className="text-xs text-muted-foreground">/100 tension</span>
      </div>
      <div className="w-full bg-muted rounded-full h-1.5 mt-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${isHigh ? "bg-red-500" : isMid ? "bg-amber-500" : "bg-green-500"}`}
          style={{ width: `${tensionScore}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground mt-1">
        {confidenceLevel === "high" ? "Confident — keep going" : confidenceLevel === "medium" ? "Moderate — stable" : "Nervous — consider slowing down"}
      </p>
    </div>
  );
}
