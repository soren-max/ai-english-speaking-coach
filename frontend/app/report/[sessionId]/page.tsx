"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { interviewService } from "@/services/interview";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Loader2,
  ArrowLeft,
  Star,
  AlertTriangle,
  Lightbulb,
  Target,
  TrendingUp,
  BookOpen,
  MessageSquare,
  Award,
} from "lucide-react";
import type {
  SessionDetail,
  ReportData,
  StarExample,
  ErrorAnalysis,
  ConversationData,
} from "@/types/interview";
import dynamic from "next/dynamic";

const RadarChart = dynamic(
  () => import("@/components/radar-chart"),
  { ssr: false, loading: () => <div className="h-80 animate-pulse bg-muted rounded-lg" /> }
);

// ── Helpers ──

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function scoreBg(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

function scoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Great";
  if (score >= 70) return "Good";
  if (score >= 60) return "Fair";
  return "Needs Work";
}

// ── Sub-components ──

function ScoreGauge({ label, score, max = 100 }: { label: string; score: number; max?: number }) {
  const pct = (score / max) * 100;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-medium">{label}</span>
        <span className={`font-semibold ${scoreColor(score)}`}>
          {Math.round(score)} <span className="text-xs text-muted-foreground">/ {max}</span>
        </span>
      </div>
      <div className="w-full bg-muted rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${scoreBg(score)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground mt-0.5">{scoreLabel(score)}</p>
    </div>
  );
}

function STARCard({
  example,
  index,
}: {
  example: StarExample;
  index: number;
}) {
  return (
    <div className="border rounded-lg p-4 space-y-3 bg-muted/30">
      <div className="flex items-center gap-2 text-sm font-semibold text-primary">
        <Award className="w-4 h-4" />
        Example {index + 1}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Situation</span>
          <p className="text-foreground/90">{example.situation}</p>
        </div>
        <div className="space-y-1">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Task</span>
          <p className="text-foreground/90">{example.task}</p>
        </div>
        <div className="space-y-1">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Action</span>
          <p className="text-foreground/90">{example.action}</p>
        </div>
        <div className="space-y-1">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Result</span>
          <p className="text-foreground/90">{example.result}</p>
        </div>
      </div>
    </div>
  );
}

function ExpressionCard({
  original,
  suggestion,
  context,
}: {
  original: string;
  suggestion: string;
  context: string;
}) {
  return (
    <div className="border rounded-lg p-4 space-y-2 bg-muted/30">
      <p className="text-xs text-muted-foreground italic">"{context}"</p>
      <div className="flex items-start gap-3 text-sm">
        <div className="flex-1">
          <span className="text-xs font-semibold text-red-500 uppercase tracking-wide">Before</span>
          <p className="line-through text-muted-foreground">{original}</p>
        </div>
        <ArrowLeft className="w-4 h-4 text-muted-foreground rotate-180 mt-5 shrink-0" />
        <div className="flex-1">
          <span className="text-xs font-semibold text-green-500 uppercase tracking-wide">After</span>
          <p className="text-foreground/90 font-medium">{suggestion}</p>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ──

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [starData, setStarData] = useState<StarExample[]>([]);
  const [errorAnalysis, setErrorAnalysis] = useState<ErrorAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await interviewService.getSession(sessionId);
        setSession(data);

        try {
          const star = await interviewService.getStarAnalysis(sessionId);
          setStarData(Array.isArray(star) ? star : []);
        } catch {
          /* optional */
        }
        try {
          const errors = await interviewService.getErrorAnalysis(sessionId);
          setErrorAnalysis(errors);
        } catch {
          /* optional */
        }
      } catch (err) {
        console.error("Failed to load report:", err);
      }
      setLoading(false);
    })();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!session || !session.report) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-lg text-muted-foreground">Report not found</p>
        <Button onClick={() => router.push("/")}>Back to Home</Button>
      </div>
    );
  }

  const report: ReportData = session.report;
  const radarData = [
    { dimension: "Fluency", score: report.fluency },
    { dimension: "Grammar", score: report.grammar },
    { dimension: "Vocabulary", score: report.vocabulary },
    { dimension: "Communication", score: report.communication },
  ];

  // Derive recommended expressions from error analysis
  const recommendedExpressions: { original: string; suggestion: string; context: string }[] = [];
  if (errorAnalysis?.common_mistakes) {
    errorAnalysis.common_mistakes.forEach((m) => {
      if (m.includes("→") || m.includes("->")) {
        const sep = m.includes("→") ? "→" : "->";
        const parts = m.split(sep);
        if (parts.length >= 2) {
          recommendedExpressions.push({
            original: parts[0].trim(),
            suggestion: parts[1].trim(),
            context: errorAnalysis.improvement_tips[0] || "General improvement area",
          });
        }
      }
    });
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Back */}
        <Button variant="ghost" className="mb-6" onClick={() => router.push("/")}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        {/* ── Header ── */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">Interview Report</h1>
          <p className="text-muted-foreground">
            {session.position} &middot; {new Date(session.start_time).toLocaleDateString()}
          </p>
        </div>

        {/* ── Overall Score ── */}
        <Card className="mb-8 text-center py-8">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-muted-foreground">Overall Score</CardTitle>
          </CardHeader>
          <CardContent>
            <span className={`text-7xl font-bold ${scoreColor(report.overall_score)}`}>
              {Math.round(report.overall_score)}
            </span>
            <span className="text-2xl text-muted-foreground">/100</span>
            <p className="text-sm text-muted-foreground mt-2">{scoreLabel(report.overall_score)}</p>
          </CardContent>
        </Card>

        {/* ── 1. 能力雷达图 ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" />
                能力雷达图
              </CardTitle>
              <p className="text-xs text-muted-foreground">Ability Radar</p>
            </CardHeader>
            <CardContent>
              <RadarChart data={radarData} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                维度评分
              </CardTitle>
              <p className="text-xs text-muted-foreground">Dimension Scores</p>
            </CardHeader>
            <CardContent className="space-y-5">
              {radarData.map((d) => (
                <ScoreGauge key={d.dimension} label={d.dimension} score={d.score} />
              ))}
            </CardContent>
          </Card>
        </div>

        {/* ── Summary ── */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-primary" />
              面试总结
            </CardTitle>
            <p className="text-xs text-muted-foreground">Summary</p>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground leading-relaxed">{report.summary}</p>
          </CardContent>
        </Card>

        {/* ── 3. 优势分析 + 4. 弱项分析 ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="border-green-200 dark:border-green-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
                <Award className="w-5 h-5" />
                优势分析
              </CardTitle>
              <p className="text-xs text-muted-foreground">Strengths Analysis</p>
            </CardHeader>
            <CardContent>
              {report.strengths.length > 0 ? (
                <ul className="space-y-3">
                  {report.strengths.map((s, i) => (
                    <li key={i} className="text-sm flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <span className="text-foreground/90">{s}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No strengths data available.</p>
              )}
            </CardContent>
          </Card>

          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-400">
                <AlertTriangle className="w-5 h-5" />
                弱项分析
              </CardTitle>
              <p className="text-xs text-muted-foreground">Weaknesses Analysis</p>
            </CardHeader>
            <CardContent>
              {report.weaknesses.length > 0 ? (
                <ul className="space-y-3">
                  {report.weaknesses.map((w, i) => (
                    <li key={i} className="text-sm flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <span className="text-foreground/90">{w}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No weaknesses data available.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* ── 5. 推荐表达 ── */}
        {recommendedExpressions.length > 0 && (
          <Card className="mb-8 border-indigo-200 dark:border-indigo-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-indigo-700 dark:text-indigo-400">
                <BookOpen className="w-5 h-5" />
                推荐表达
              </CardTitle>
              <p className="text-xs text-muted-foreground">Recommended Expressions</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {recommendedExpressions.map((expr, i) => (
                <ExpressionCard key={i} {...expr} />
              ))}
            </CardContent>
          </Card>
        )}

        {/* ── 2. STAR分析展示 ── */}
        {starData.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-500" />
                STAR 分析展示
              </CardTitle>
              <p className="text-xs text-muted-foreground">STAR Method Analysis</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {starData.map((star, i) => (
                <STARCard key={i} example={star} index={i} />
              ))}
            </CardContent>
          </Card>
        )}

        {/* ── Error Analysis (integrated into 弱项 + 推荐表达) ── */}
        {errorAnalysis && errorAnalysis.vocabulary_gaps.length > 0 && (
          <Card className="mb-8 border-orange-200 dark:border-orange-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-700 dark:text-orange-400">
                <BookOpen className="w-5 h-5" />
                词汇缺口
              </CardTitle>
              <p className="text-xs text-muted-foreground">Vocabulary Gaps</p>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {errorAnalysis.vocabulary_gaps.map((v, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded-full text-xs font-medium"
                  >
                    {v}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* ── Error Analysis: Common Mistakes ── */}
        {errorAnalysis && errorAnalysis.common_mistakes.length > 0 && (
          <Card className="mb-8 border-rose-200 dark:border-rose-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-rose-700 dark:text-rose-400">
                <AlertTriangle className="w-5 h-5" />
                常见错误
              </CardTitle>
              <p className="text-xs text-muted-foreground">Common Mistakes</p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {errorAnalysis.common_mistakes.map((m, i) => (
                  <li key={i} className="text-sm flex items-start gap-2 text-muted-foreground">
                    <span className="text-rose-400 mt-1">&#8226;</span>
                    {m}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* ── 6. 学习建议 (combined from report.suggestions + error analysis tips) ── */}
        <Card className="mb-8 border-blue-200 dark:border-blue-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
              <Lightbulb className="w-5 h-5" />
              学习建议
            </CardTitle>
            <p className="text-xs text-muted-foreground">Learning Suggestions</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Report suggestions */}
              {report.suggestions.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-2 text-foreground/80">Improvement Areas</h3>
                  <ul className="space-y-2">
                    {report.suggestions.map((s, i) => (
                      <li key={i} className="text-sm flex items-start gap-3">
                        <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <span className="text-foreground/90">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Error analysis improvement tips */}
              {errorAnalysis && errorAnalysis.improvement_tips.length > 0 && (
                <div className="pt-3 border-t">
                  <h3 className="text-sm font-semibold mb-2 text-foreground/80">Language Tips</h3>
                  <ul className="space-y-1">
                    {errorAnalysis.improvement_tips.map((t, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-blue-400 mt-1">&#8226;</span>
                        {t}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ── Actions ── */}
        <div className="flex justify-center gap-4 pb-12">
          <Button variant="outline" onClick={() => router.push("/")}>
            Practice Again
          </Button>
          <Button onClick={() => window.print()}>
            Print Report
          </Button>
        </div>
      </div>
    </div>
  );
}
