"use client";

/** Mini live score bar — shows after each AI response in interview room */
import { TrendingUp } from "lucide-react";

interface MiniScoreProps {
  fluency?: number;
  grammar?: number;
  vocabulary?: number;
  communication?: number;
}

export default function MiniScoreBar({ fluency, grammar, vocabulary, communication }: MiniScoreProps) {
  const hasData = fluency !== undefined;
  if (!hasData) return null;

  const avg = Math.round((fluency! + grammar! + vocabulary! + communication!) / 4);

  return (
    <div className="fixed bottom-24 right-4 z-50 w-48 bg-card border rounded-lg shadow-lg p-3 animate-in slide-in-from-right">
      <div className="flex items-center gap-2 mb-2">
        <TrendingUp className="w-3.5 h-3.5 text-primary" />
        <span className="text-xs font-semibold">Live Score</span>
        <span className="text-xs font-bold ml-auto">{avg}</span>
      </div>
      {[
        { label: "Fluency", value: fluency! },
        { label: "Grammar", value: grammar! },
        { label: "Vocab", value: vocabulary! },
        { label: "Comm", value: communication! },
      ].map((s) => (
        <div key={s.label} className="flex items-center gap-1.5 mb-1">
          <span className="text-[10px] text-muted-foreground w-8">{s.label}</span>
          <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-500"
              style={{ width: `${Math.min(s.value, 100)}%` }}
            />
          </div>
          <span className="text-[10px] font-medium w-5 text-right">{Math.round(s.value)}</span>
        </div>
      ))}
    </div>
  );
}
