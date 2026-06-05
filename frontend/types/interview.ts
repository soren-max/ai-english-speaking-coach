export interface SessionStartRequest {
  position: string;
  resume_text?: string;
}

export interface SessionStartResponse {
  session_id: string;
  question: string;
}

export interface SessionMessageRequest {
  session_id: string;
  content: string;
}

export interface SessionMessageResponse {
  reply: string;
}

export interface SessionEndResponse {
  session_id: string;
  report: ReportData;
}

export interface ReportData {
  id: string;
  session_id: string;
  overall_score: number;
  fluency: number;
  grammar: number;
  vocabulary: number;
  communication: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

export interface ConversationData {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface SessionDetail {
  id: string;
  user_id: string;
  position: string;
  status: string;
  start_time: string;
  end_time: string | null;
  overall_score: number | null;
  conversations: ConversationData[];
  report: ReportData | null;
}

export interface StarExample {
  situation: string;
  task: string;
  action: string;
  result: string;
}

export interface ErrorAnalysis {
  error_count: number;
  common_mistakes: string[];
  improvement_tips: string[];
  vocabulary_gaps: string[];
}
