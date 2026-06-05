/** Emotion analysis types. */
export interface FillerInfo {
  word: string;
  count: number;
}
export interface EmotionAnalysis {
  tension_score: number;
  confidence_level: "low" | "medium" | "high";
  filler_word_count: number;
  filler_density: number;
  fillers_found: FillerInfo[];
  hesitation_found: string[];
  confidence_signals: string[];
  weak_claims: string[];
  word_count: number;
  suggestions: string[];
  adapted_difficulty: string;
}
export interface BatchEmotionResult {
  overall_tension: number;
  trend: string;
  analyses: EmotionAnalysis[];
}

/** I18n types. */
export interface TermLookup {
  term: string;
  chinese: string | null;
  found: boolean;
}
export interface StageHint {
  title: string;
  hint: string;
  tip: string;
}
export interface QuestionHint {
  question: string;
  strategy_hint: string | null;
  phrase_hint: string | null;
}
export interface CompanyTip {
  company: string;
  focus: string;
  tip: string;
}

/** Company profile types. */
export interface CompanySummary {
  id: string;
  name: string;
  description: string;
  focus_areas: string[];
  difficulty_baseline: number;
}
export interface CompanyProfile extends CompanySummary {
  question_style: string;
  values: string[];
  interview_flow: string[];
}
export interface CompanyInterviewPlan {
  company: string;
  position: string;
  difficulty: number;
  focus_areas: string[];
  values: string[];
  interview_flow: string[];
  question_style: string;
  practice_questions: {
    question: string;
    topic: string;
    difficulty: number;
    source: string;
  }[];
}
