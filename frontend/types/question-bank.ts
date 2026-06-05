/** Question Bank types — curated interview questions. */

export interface BankQuestion {
  question: string;
  topic: string;
  difficulty: number;
  source: string;
  updated?: string;
}

export interface QuestionBankResponse {
  position: string;
  count: number;
  questions: BankQuestion[];
}

export interface BankStats {
  total_questions: number;
  positions: number;
  by_position: Record<string, number>;
  by_topic: Record<string, number>;
  last_updated: string | null;
}

export interface RefreshResponse {
  message: string;
  sources_checked: number;
  total: number;
}
