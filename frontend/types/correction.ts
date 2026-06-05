/** Correction types — real-time expression feedback. */

export interface CorrectionData {
  has_correction: boolean;
  original?: string;
  corrected?: string;
  explanation?: string;
  type?: "grammar" | "vocabulary" | "style" | "fluency";
  tts_text?: string;
}
