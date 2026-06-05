"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { interviewService } from "@/services/interview";
import { Mic, Send, Square, Loader2 } from "lucide-react";
import type { ConversationData } from "@/types/interview";

// Speech recognition hook — from voice/ module, returns { isListening, transcript, start, stop }
function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<globalThis.SpeechRecognition | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
  }, []);

  const start = useCallback(() => {
    if (recognitionRef.current) {
      setTranscript("");
      setIsListening(true);
      recognitionRef.current.start();
    }
  }, []);

  const stop = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  return { isListening, transcript, start, stop };
}

// Text-to-speech function — from voice/ module
function speak(text: string) {
  if (typeof window === "undefined") return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

export default function InterviewRoom() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [messages, setMessages] = useState<ConversationData[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [ended, setEnded] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);

  const { isListening, transcript, start: startMic, stop: stopMic } = useSpeechRecognition();

  // Load session on mount
  useEffect(() => {
    (async () => {
      try {
        const session = await interviewService.getSession(sessionId);
        setMessages(session.conversations);
      } catch {
        // Session might not exist yet (just created) — that's ok
      }
      setLoading(false);
    })();
  }, [sessionId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // When speech transcript arrives, auto-submit it
  useEffect(() => {
    if (transcript) {
      setInput(transcript);
      handleSend(transcript);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcript]);

  const handleSend = async (text?: string) => {
    const content = text ?? input;
    if (!content.trim() || sending || ended) return;

    const userMsg: ConversationData = {
      id: crypto.randomUUID(),
      session_id: sessionId,
      role: "user",
      content: content.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      const result = await interviewService.sendMessage(sessionId, content.trim());
      const aiMsg: ConversationData = {
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: "assistant",
        content: result.reply,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      speak(result.reply);
    } catch (err) {
      console.error("Send failed:", err);
    }
    setSending(false);
  };

  const handleEnd = async () => {
    if (ended) return;
    setEnded(true);
    try {
      const result = await interviewService.endSession(sessionId, input);
      setInput("");
      router.push(`/report/${sessionId}`);
    } catch (err) {
      console.error("End failed:", err);
      setEnded(false);
    }
  };

  const toggleMic = () => {
    if (isListening) {
      stopMic();
    } else {
      startMic();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-4 py-3 flex items-center justify-between bg-card">
        <h1 className="font-semibold text-lg">Interview Session</h1>
        <Button variant="destructive" size="sm" onClick={handleEnd} disabled={ended}>
          <Square className="w-4 h-4 mr-2" />
          {ended ? "Ending..." : "End Interview"}
        </Button>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-20">
            <p>Waiting for the first question...</p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <Card
              className={`max-w-[80%] px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <p className="text-xs opacity-60 mt-1">
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </Card>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <Card className="bg-muted px-4 py-3">
              <Loader2 className="w-5 h-5 animate-spin" />
            </Card>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      {/* Input area */}
      <div className="border-t bg-card px-4 py-4">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <Button
            variant={isListening ? "destructive" : "outline"}
            size="icon"
            onClick={toggleMic}
            title={isListening ? "Stop recording" : "Start recording"}
          >
            <Mic className="w-5 h-5" />
          </Button>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Type your answer..."
            disabled={sending || ended}
            className="flex-1"
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || sending || ended}
          >
            <Send className="w-4 h-4 mr-2" />
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
