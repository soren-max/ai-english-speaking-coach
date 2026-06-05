"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { interviewService } from "@/services/interview";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, ArrowLeft, Play, Pause, SkipBack, SkipForward, MessageSquare, Brain, TrendingUp } from "lucide-react";
import type { SessionDetail, ConversationData } from "@/types/interview";

export default function ReplayPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await interviewService.getSession(sessionId);
        setSession(data);
      } catch (err) {
        console.error("Failed to load session:", err);
      }
      setLoading(false);
    })();
  }, [sessionId]);

  // Auto-play
  useEffect(() => {
    if (!isPlaying || !session) return;
    const msgs = session.conversations;
    if (currentIndex >= msgs.length - 1) {
      setIsPlaying(false);
      return;
    }
    timerRef.current = setTimeout(() => {
      setCurrentIndex((i) => Math.min(i + 1, msgs.length - 1));
    }, 2000);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [isPlaying, currentIndex, session]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-lg text-muted-foreground">Session not found</p>
        <Button onClick={() => router.push("/")}>Back to Home</Button>
      </div>
    );
  }

  const msgs: ConversationData[] = session.conversations;
  const visible = msgs.slice(0, currentIndex + 1);
  const progress = msgs.length > 0 ? ((currentIndex + 1) / msgs.length) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => router.push(`/report/${sessionId}`)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Report
          </Button>
          <div className="text-right">
            <h1 className="text-lg font-bold">Interview Replay</h1>
            <p className="text-sm text-muted-foreground">{session.position}</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-muted rounded-full h-2 mb-6">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Messages */}
        <div className="space-y-4 mb-8">
          {visible.map((msg, i) => (
            <div
              key={msg.id || i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300`}
            >
              <Card className={`max-w-[80%] px-4 py-3 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                <div className="flex items-center gap-2 mb-1">
                  {msg.role === "assistant" ? (
                    <Brain className="w-4 h-4" />
                  ) : (
                    <MessageSquare className="w-4 h-4" />
                  )}
                  <span className="text-xs font-semibold opacity-70">
                    {msg.role === "assistant" ? "Interviewer" : "You"}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs opacity-50 mt-1">
                  Turn {Math.floor(i / 2) + 1}
                </p>
              </Card>
            </div>
          ))}

          {currentIndex < msgs.length - 1 && isPlaying && (
            <div className="flex justify-start">
              <Card className="bg-muted/50 px-4 py-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Controls */}
        <Card className="sticky bottom-4">
          <CardContent className="flex items-center justify-center gap-4 py-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentIndex(0)}
              disabled={currentIndex === 0}
            >
              <SkipBack className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentIndex((i) => Math.max(i - 1, 0))}
              disabled={currentIndex === 0}
            >
              <SkipForward className="w-5 h-5 rotate-180" />
            </Button>
            <Button
              variant={isPlaying ? "secondary" : "default"}
              size="icon"
              className="w-12 h-12 rounded-full"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentIndex((i) => Math.min(i + 1, msgs.length - 1))}
              disabled={currentIndex >= msgs.length - 1}
            >
              <SkipForward className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCurrentIndex(msgs.length - 1)}
              disabled={currentIndex >= msgs.length - 1}
              title="Skip to end"
            >
              <div className="relative">
                <SkipForward className="w-4 h-4" />
                <span className="absolute -right-0.5 -top-0.5 text-[8px] font-bold">&gt;</span>
              </div>
            </Button>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="flex justify-center gap-6 mt-4 text-sm text-muted-foreground">
          <span>{msgs.length} messages</span>
          <span>Turn {Math.floor(currentIndex / 2) + 1}/{Math.ceil(msgs.length / 2)}</span>
          <span>{Math.round(progress)}% complete</span>
        </div>
      </div>
    </div>
  );
}
