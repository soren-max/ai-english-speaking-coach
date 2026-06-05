import { apiClient } from "./api-client";
import type {
  SharedAnswer,
  ShareDetail,
  CommunityFeed,
  CommunityStats,
  PeerReview,
} from "@/types/community";

export const communityService = {
  /** Share an interview answer to the community. */
  async shareAnswer(
    sessionId: string,
    question: string,
    answer: string,
    position: string,
    isAnonymous = true
  ): Promise<SharedAnswer> {
    const params = new URLSearchParams({
      session_id: sessionId,
      question,
      answer,
      position,
      is_anonymous: String(isAnonymous),
    });
    return apiClient.post<SharedAnswer>(
      `/community/share?${params.toString()}`,
      {}
    );
  },

  /** Get community feed of shared answers. */
  async getFeed(
    options?: { position?: string; page?: number; pageSize?: number }
  ): Promise<CommunityFeed> {
    const params = new URLSearchParams();
    if (options?.position) params.set("position", options.position);
    if (options?.page) params.set("page", String(options.page));
    if (options?.pageSize) params.set("page_size", String(options.pageSize));
    return apiClient.get<CommunityFeed>(
      `/community/shares?${params.toString()}`
    );
  },

  /** Get a shared answer with AI review + peer reviews. */
  async getShareDetail(shareId: string): Promise<ShareDetail> {
    return apiClient.get<ShareDetail>(`/community/share/${shareId}`);
  },

  /** Add a peer review to a shared answer. */
  async addReview(
    shareId: string,
    rating: number,
    comment: string,
    reviewerName = "Anonymous Peer"
  ): Promise<PeerReview> {
    const params = new URLSearchParams({
      rating: String(rating),
      comment,
      reviewer_name: reviewerName,
    });
    return apiClient.post<PeerReview>(
      `/community/share/${shareId}/review?${params.toString()}`,
      {}
    );
  },

  /** Get community statistics. */
  async getStats(): Promise<CommunityStats> {
    return apiClient.get<CommunityStats>("/community/stats");
  },
};
