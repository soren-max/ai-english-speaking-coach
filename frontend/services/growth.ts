import { apiClient } from "./api-client";
import type { GrowthHistory } from "@/types/growth";

export const growthService = {
  /**
   * Fetch historical interview scores for growth curve visualization.
   * Returns scores ordered by date, one entry per completed interview.
   */
  async getHistory(): Promise<GrowthHistory> {
    return apiClient.get<GrowthHistory>("/growth/history");
  },
};
