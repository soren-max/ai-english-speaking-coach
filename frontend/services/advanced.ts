import { apiClient } from "./api-client";
import type {
  EmotionAnalysis,
  BatchEmotionResult,
  TermLookup,
  StageHint,
  QuestionHint,
  CompanySummary,
  CompanyProfile,
  CompanyInterviewPlan,
} from "@/types/advanced";

export const emotionService = {
  /** Analyze a single answer for tension and confidence. */
  async analyze(text: string): Promise<EmotionAnalysis> {
    return apiClient.post<EmotionAnalysis>(
      `/emotion/analyze?text=${encodeURIComponent(text)}`,
      {}
    );
  },
  /** Analyze multiple answers for tension trends. */
  async batch(answers: string[]): Promise<BatchEmotionResult> {
    const params = answers.map((a) => `answers=${encodeURIComponent(a)}`).join("&");
    return apiClient.post<BatchEmotionResult>(`/emotion/batch?${params}`, {});
  },
};

export const i18nService = {
  /** Translate an interview term to Chinese. */
  async lookupTerm(term: string): Promise<TermLookup> {
    return apiClient.get<TermLookup>(`/i18n/term?term=${encodeURIComponent(term)}`);
  },
  /** Get interview stage hints in Chinese. */
  async stageHint(stage: number): Promise<StageHint> {
    return apiClient.get<StageHint>(`/i18n/stage/${stage}`);
  },
  /** Generate Chinese hint for any interview question. */
  async questionHint(question: string): Promise<QuestionHint> {
    return apiClient.get<QuestionHint>(
      `/i18n/hint?question=${encodeURIComponent(question)}`
    );
  },
};

export const companyService = {
  /** List all supported company profiles. */
  async list(): Promise<{ companies: CompanySummary[] }> {
    return apiClient.get<{ companies: CompanySummary[] }>("/company/list");
  },
  /** Get full company profile. */
  async getProfile(companyId: string): Promise<CompanyProfile> {
    return apiClient.get<CompanyProfile>(`/company/${companyId}`);
  },
  /** Get interview questions tailored to a company's style. */
  async getQuestions(
    companyId: string,
    position = "Software Engineer",
    limit = 5
  ) {
    return apiClient.get(
      `/company/${companyId}/questions?position=${encodeURIComponent(position)}&limit=${limit}`
    );
  },
  /** Generate a complete mock interview plan. */
  async getPlan(
    companyId: string,
    position = "Software Engineer"
  ): Promise<CompanyInterviewPlan> {
    return apiClient.get<CompanyInterviewPlan>(
      `/company/${companyId}/plan?position=${encodeURIComponent(position)}`
    );
  },
};
