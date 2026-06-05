"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { interviewService } from "@/services/interview";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Briefcase, Code, Cpu } from "lucide-react";

const ROLES = [
  {
    id: "backend",
    title: "Backend Engineer",
    description: "System design, APIs, databases, scalability",
    icon: Briefcase,
  },
  {
    id: "software",
    title: "Software Engineer",
    description: "Algorithms, data structures, OOP, coding",
    icon: Code,
  },
  {
    id: "ai",
    title: "AI Engineer",
    description: "ML, NLP, LLMs, model deployment",
    icon: Cpu,
  },
];

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);

  const handleStart = async (role: string) => {
    setLoading(role);
    try {
      const result = await interviewService.startSession(role);
      router.push(`/interview/${result.session_id}`);
    } catch (err) {
      console.error("Failed to start session:", err);
      setLoading(null);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      <div className="container mx-auto px-4 py-20">
        {/* Hero */}
        <div className="text-center mb-16 space-y-4">
          <h1 className="text-5xl font-bold tracking-tight">InterviewGPT</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            AI-powered interview practice. Choose your role and start practicing
            with a senior interviewer.
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {ROLES.map((role) => {
            const Icon = role.icon;
            const isBusy = loading === role.id;
            return (
              <Card
                key={role.id}
                className="relative overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer group"
                onClick={() => !isBusy && handleStart(role.title)}
              >
                <CardHeader className="pb-3">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{role.title}</CardTitle>
                  <CardDescription>{role.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    className="w-full"
                    disabled={isBusy}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleStart(role.title);
                    }}
                  >
                    {isBusy ? "Starting..." : "Start Interview"}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </main>
  );
}
