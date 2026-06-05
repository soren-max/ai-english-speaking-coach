/** Community / Peer Review types. */

export interface AIReview {
  score: number;
  strengths: string[];
  improvements: string[];
  star_completeness: {
    situation: boolean;
    task: boolean;
    action: boolean;
    result: boolean;
  };
  summary: string;
}

export interface SharedAnswer {
  id: string;
  session_id: string;
  question: string;
  answer: string;
  position: string;
  is_anonymous: boolean;
  shared_at: string;
  view_count: number;
  ai_review: AIReview | null;
}

export interface PeerReview {
  id: string;
  share_id: string;
  reviewer_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface ShareDetail extends SharedAnswer {
  reviews: PeerReview[];
  avg_rating: number;
  review_count: number;
}

export interface CommunityFeed {
  items: SharedAnswer[];
  total: number;
  page: number;
  page_size: number;
}

export interface CommunityStats {
  total_shares: number;
  total_reviews: number;
  positions: Record<string, number>;
  avg_reviews_per_share: number;
}
