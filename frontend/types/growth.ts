/** Growth tracking types — historical score comparison. */

export interface ScoreSnapshot {
  date: string;
  position: string;
  overall_score: number;
  fluency: number;
  grammar: number;
  vocabulary: number;
  communication: number;
}

export interface GrowthHistory {
  history: ScoreSnapshot[];
  total_sessions: number;
}

/** Data shape for the comparative radar chart. */
export interface RadarComparison {
  dimension: string;
  [sessionLabel: string]: number | string;
}
