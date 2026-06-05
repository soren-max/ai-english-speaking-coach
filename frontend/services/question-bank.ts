import { apiClient } from "./api-client";
import type {
  QuestionBankResponse,
  BankStats,
  RefreshResponse,
} from "@/types/question-bank";

export const questionBankService = {
  /**
   * Get interview questions for a position.
   * Optional filters: topic, difficulty (1-5), limit.
   */
  async getQuestions(
    position: string,
    options?: { topic?: string; difficulty?: number; limit?: number }
  ): Promise<QuestionBankResponse> {
    const params = new URLSearchParams();
    if (options?.topic) params.set("topic", options.topic);
    if (options?.difficulty) params.set("difficulty", String(options.difficulty));
    if (options?.limit) params.set("limit", String(options.limit));
    const qs = params.toString();
    return apiClient.get<QuestionBankResponse>(
      `/question-bank/${encodeURIComponent(position)}${qs ? `?${qs}` : ""}`
    );
  },

  /** Get question bank statistics. */
  async getStats(): Promise<BankStats> {
    return apiClient.get<BankStats>("/question-bank/stats");
  },

  /** Trigger a refresh from web sources. */
  async refresh(): Promise<RefreshResponse> {
    return apiClient.post<RefreshResponse>("/question-bank/refresh", {});
  },
};
