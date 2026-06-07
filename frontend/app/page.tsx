"use client";

import { useRouter } from "next/navigation";
import { useState, useRef } from "react";
import { interviewService } from "@/services/interview";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Briefcase, Code, Cpu, Upload, FileText, X } from "lucide-react";

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
  const [resumeText, setResumeText] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setResumeText(text);
    };
    reader.readAsText(file);
  };

  const clearResume = () => {
    setResumeText("");
    setFileName(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleStart = async (role: string) => {
    setLoading(role);
    try {
      const result = await interviewService.startSession(role, resumeText);
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
        <div className="text-center mb-12 space-y-4">
          <h1 className="text-5xl font-bold tracking-tight">InterviewGPT</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            AI-powered interview practice. Upload your resume, choose your role,
            and get interviewed by a senior AI interviewer.
          </p>
        </div>

        {/* Resume Upload Section */}
        <div className="max-w-2xl mx-auto mb-10">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Upload Your Resume
              </CardTitle>
              <CardDescription>
                Paste your resume or upload a text file — AI will tailor questions to your experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* File upload button */}
              <div className="flex items-center gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,.pdf"
                  className="hidden"
                  onChange={handleFileUpload}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload File
                </Button>
                {fileName && (
                  <span className="text-sm text-muted-foreground flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    {fileName}
                    <button onClick={clearResume} className="ml-1 hover:text-foreground">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                )}
              </div>

              {/* Resume text area */}
              <Textarea
                placeholder="Or paste your resume text here... (optional)"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                className="min-h-[120px] text-sm"
              />
              {resumeText && (
                <p className="text-xs text-muted-foreground">
                  {resumeText.length} characters &middot; AI will tailor questions to your background
                </p>
              )}
            </CardContent>
          </Card>
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
