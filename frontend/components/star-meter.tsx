"use client";

/** STARMeter — per-answer STAR completeness visualization */
import { CheckCircle, XCircle } from "lucide-react";

interface StarScore {
  present: boolean;
  score: number;
  text: string;
}

interface STARMeterProps {
  situation?: StarScore;
  task?: StarScore;
  action?: StarScore;
  result?: StarScore;
  size?: "sm" | "md";
}

const COMPONENTS = ["situation", "task", "action", "result"] as const;
const LABELS: Record<string, string> = {
  situation: "Situation",
  task: "Task",
  action: "Action",
  result: "Result",
};

export default function STARMeter({ situation, task, action, result, size = "sm" }: STARMeterProps) {
  const scores = { situation, task, action, result };

  if (size === "sm") {
    const presentCount = COMPONENTS.filter((c) => scores[c]?.present).length;
    return (
      <div className="inline-flex items-center gap-1">
        {COMPONENTS.map((c) => {
          const s = scores[c];
          const ok = s?.present;
          return (
            <div
              key={c}
              className={`w-5 h-5 rounded-full flex items-center justify-center ${
                ok ? "bg-green-100 dark:bg-green-900/40" : "bg-red-100 dark:bg-red-900/40"
              }`}
              title={`${LABELS[c]}: ${ok ? s?.score + "/10" : "Missing"}`}
            >
              {ok ? (
                <CheckCircle className="w-3 h-3 text-green-600 dark:text-green-400" />
              ) : (
                <XCircle className="w-3 h-3 text-red-500" />
              )}
            </div>
          );
        })}
        <span className="text-xs text-muted-foreground ml-1">{presentCount}/4</span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {COMPONENTS.map((c) => {
        const s = scores[c];
        const ok = s?.present;
        return (
          <div key={c} className="flex items-center gap-3">
            <span className="text-xs font-medium w-16 text-muted-foreground">{LABELS[c]}</span>
            {ok ? (
              <div className="flex-1 flex items-center gap-2">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full transition-all duration-500"
                    style={{ width: `${(s?.score || 0) * 10}%` }}
                  />
                </div>
                <span className="text-xs font-semibold text-green-600 w-6">{s?.score}/10</span>
              </div>
            ) : (
              <div className="flex-1 flex items-center gap-2">
                <div className="flex-1 h-2 bg-red-100 dark:bg-red-900/30 rounded-full" />
                <span className="text-xs text-red-500 font-medium w-6">Missing</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
