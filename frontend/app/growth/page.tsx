"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Loader2,
  TrendingUp,
  ArrowLeft,
  Target,
  BarChart3,
  LineChart,
} from "lucide-react";
import { growthService } from "@/services/growth";
import type { ScoreSnapshot, RadarComparison } from "@/types/growth";
import dynamic from "next/dynamic";

const GrowthRadar = dynamic(
  () => import("@/components/growth-radar"),
  { ssr: false, loading: () => <div className="h-80 animate-pulse bg-muted rounded-lg" /> }
);

const DIMENSIONS = ["fluency", "grammar", "vocabulary", "communication"] as const;
const DIM_LABELS: Record<string, string> = {
  fluency: "Fluency",
  grammar: "Grammar",
  vocabulary: "Vocabulary",
  communication: "Communication",
};

function label(date: string, idx: number): string {
  return `#${idx + 1} (${date})`;
}

export default function GrowthPage() {
  const router = useRouter();
  const [data, setData] = useState<ScoreSnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await growthService.getHistory();
        setData(res.history);
      } catch {
        // no data yet
      }
      setLoading(false);
    })();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const radarData: RadarComparison[] = DIMENSIONS.map((dim) => {
    const entry: RadarComparison = { dimension: DIM_LABELS[dim] };
    data.forEach((snap, i) => {
      entry[label(snap.date, i)] = snap[dim];
    });
    return entry;
  });

  const COLORS = [
    "hsl(142, 76%, 36%)",
    "hsl(217, 91%, 60%)",
    "hsl(271, 81%, 56%)",
    "hsl(24, 95%, 53%)",
    "hsl(0, 72%, 51%)",
    "hsl(200, 100%, 50%)",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <Button variant="ghost" className="mb-6" onClick={() => router.push("/")}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-3">
            <TrendingUp className="w-8 h-8 text-primary" />
            Growth Curve
          </h1>
          <p className="text-muted-foreground">
            Track your ability improvement across interviews
          </p>
        </div>

        {data.length === 0 ? (
          <Card className="text-center py-16">
            <CardContent>
              <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg text-muted-foreground mb-4">
                No interview history yet. Complete your first interview to see growth data.
              </p>
              <Button onClick={() => router.push("/")}>
                Start Your First Interview
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Summary stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {DIMENSIONS.map((dim) => {
                const first = data[0][dim];
                const last = data[data.length - 1][dim];
                const change = (last - first).toFixed(1);
                const improved = Number(change) >= 0;
                return (
                  <Card key={dim}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-muted-foreground">
                        {DIM_LABELS[dim]}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold">{Math.round(last)}</span>
                        <span className={`text-sm font-medium ${improved ? "text-green-500" : "text-red-500"}`}>
                          {improved ? "↑" : "↓"} {Math.abs(Number(change))}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        from {Math.round(first)} ({data.length} sessions)
                      </p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Comparative radar chart */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-primary" />
                  Score Comparison Across Sessions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <GrowthRadar data={radarData} colors={COLORS.slice(0, data.length)} />
              </CardContent>
            </Card>

            {/* Timeline table */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5 text-primary" />
                  Detailed History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 pr-4">#</th>
                        <th className="pb-2 pr-4">Date</th>
                        <th className="pb-2 pr-4">Position</th>
                        <th className="pb-2 pr-4 text-right">Overall</th>
                        <th className="pb-2 pr-4 text-right">Fluency</th>
                        <th className="pb-2 pr-4 text-right">Grammar</th>
                        <th className="pb-2 pr-4 text-right">Vocab</th>
                        <th className="pb-2 text-right">Comm</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((snap, i) => (
                        <tr key={i} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="py-2 pr-4 font-medium">{i + 1}</td>
                          <td className="py-2 pr-4">{snap.date}</td>
                          <td className="py-2 pr-4">{snap.position}</td>
                          <td className="py-2 pr-4 text-right font-semibold">{Math.round(snap.overall_score)}</td>
                          <td className="py-2 pr-4 text-right">{Math.round(snap.fluency)}</td>
                          <td className="py-2 pr-4 text-right">{Math.round(snap.grammar)}</td>
                          <td className="py-2 pr-4 text-right">{Math.round(snap.vocabulary)}</td>
                          <td className="py-2 text-right">{Math.round(snap.communication)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Radar chart legend */}
            <div className="flex flex-wrap gap-4 justify-center mb-8">
              {data.map((snap, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  {label(snap.date, i)}
                </div>
              ))}
            </div>
          </>
        )}

        <div className="flex justify-center pb-12">
          <Button variant="outline" onClick={() => router.push("/")}>
            Practice Again
          </Button>
        </div>
      </div>
    </div>
  );
}
