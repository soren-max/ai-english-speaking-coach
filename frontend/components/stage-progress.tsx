"use client";

/** Interview stage progress bar — shows 5 stages progression */
import { Check, Circle } from "lucide-react";

const STAGES = [
  "Self-Intro",
  "Project",
  "Technical",
  "System Design",
  "Behavioral",
];

interface StageProgressProps {
  currentStage: number; // 1-5
}

export default function StageProgress({ currentStage }: StageProgressProps) {
  return (
    <div className="w-full max-w-lg mx-auto mb-4">
      <div className="flex items-center justify-between relative">
        {/* Connector line */}
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-muted -translate-y-1/2">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${((currentStage - 1) / (STAGES.length - 1)) * 100}%` }}
          />
        </div>

        {STAGES.map((label, i) => {
          const idx = i + 1;
          const done = idx < currentStage;
          const active = idx === currentStage;
          return (
            <div key={label} className="flex flex-col items-center gap-1 z-10">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  done
                    ? "bg-primary text-primary-foreground"
                    : active
                    ? "bg-primary/20 text-primary border-2 border-primary"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {done ? <Check className="w-4 h-4" /> : idx}
              </div>
              <span
                className={`text-[10px] font-medium ${
                  active ? "text-primary" : "text-muted-foreground"
                }`}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
