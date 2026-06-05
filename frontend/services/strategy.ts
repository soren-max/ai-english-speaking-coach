import { apiClient } from "./api-client";
import type { StrategyData } from "@/types/strategy";

/**
 * StrategyService — fetches interview answer strategy analysis.
 *
 * Usage:
 *   import { strategyService } from "@/services/strategy";
 *   const analysis = await strategyService.getAnalysis(sessionId);
 */
export const strategyService = {
  /**
   * Get strategy analysis (STAR completeness, technical depth, project logic).
   * Call after the interview is complete or after several answers.
   */
  async getAnalysis(sessionId: string): Promise<StrategyData> {
    return apiClient.get<StrategyData>(`/strategy/${sessionId}`);
  },
};
