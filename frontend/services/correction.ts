import { apiClient } from "./api-client";
import type { CorrectionData } from "@/types/correction";

/**
 * CorrectionService — fetches real-time expression corrections.
 *
 * Usage in Interview Room:
 *
 *   import { correctionService } from "@/services/correction";
 *   import { speak } from "@/voice/text-to-speech";
 *
 *   // After receiving AI reply:
 *   const corr = await correctionService.getLatest(sessionId);
 *   if (corr.has_correction && corr.tts_text) {
 *     speak(corr.tts_text);  // "Try saying it like this instead..."
 *   }
 */
export const correctionService = {
  /**
   * Get the latest expression correction for a session.
   * Call this AFTER each sendMessage().
   */
  async getLatest(sessionId: string): Promise<CorrectionData> {
    return apiClient.get<CorrectionData>(`/correction/${sessionId}`);
  },
};
