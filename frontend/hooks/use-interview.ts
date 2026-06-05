"use client";

import { useState, useCallback } from "react";
import { interviewService } from "@/services/interview";
import type {
  ConversationData,
  SessionDetail,
} from "@/types/interview";

export function useInterview(sessionId: string) {
  const [messages, setMessages] = useState<ConversationData[]>([]);
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    setLoading(true);
    try {
      const data = await interviewService.getSession(sessionId);
      setSession(data);
      setMessages(data.conversations);
    } catch (err) {
      setError("Failed to load session");
    }
    setLoading(false);
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMsg: ConversationData = {
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setSending(true);

      try {
        const result = await interviewService.sendMessage(sessionId, content);
        const aiMsg: ConversationData = {
          id: crypto.randomUUID(),
          session_id: sessionId,
          role: "assistant",
          content: result.reply,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, aiMsg]);
        return result.reply;
      } catch {
        setError("Failed to send message");
        return null;
      } finally {
        setSending(false);
      }
    },
    [sessionId]
  );

  const endSession = useCallback(
    async (finalMessage = "") => {
      try {
        return await interviewService.endSession(sessionId, finalMessage);
      } catch {
        setError("Failed to end session");
        return null;
      }
    },
    [sessionId]
  );

  return {
    messages,
    session,
    sending,
    loading,
    error,
    loadSession,
    sendMessage,
    endSession,
  };
}
