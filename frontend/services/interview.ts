import { apiClient } from "./api-client";
import type {
  SessionStartRequest,
  SessionStartResponse,
  SessionMessageRequest,
  SessionMessageResponse,
  SessionEndResponse,
  SessionDetail,
  StarExample,
  ErrorAnalysis,
} from "@/types/interview";

export const interviewService = {
  async startSession(position: string, resumeText = ""): Promise<SessionStartResponse> {
    return apiClient.post<SessionStartResponse>("/session/start", {
      position,
      resume_text: resumeText,
    } satisfies SessionStartRequest);
  },

  async sendMessage(
    sessionId: string,
    content: string
  ): Promise<SessionMessageResponse> {
    return apiClient.post<SessionMessageResponse>("/session/message", {
      session_id: sessionId,
      content,
    } satisfies SessionMessageRequest);
  },

  async endSession(
    sessionId: string,
    finalMessage = ""
  ): Promise<SessionEndResponse> {
    return apiClient.post<SessionEndResponse>("/session/end", {
      session_id: sessionId,
      content: finalMessage,
    } satisfies SessionMessageRequest);
  },

  async getSession(sessionId: string): Promise<SessionDetail> {
    return apiClient.get<SessionDetail>(`/session/${sessionId}`);
  },

  async getStarAnalysis(sessionId: string): Promise<StarExample[]> {
    // In a real app, this would call a dedicated endpoint.
    // For now, we derive from the session report.
    return apiClient.get<StarExample[]>(`/session/${sessionId}/star`);
  },

  async getErrorAnalysis(sessionId: string): Promise<ErrorAnalysis> {
    return apiClient.get<ErrorAnalysis>(`/session/${sessionId}/errors`);
  },
};
