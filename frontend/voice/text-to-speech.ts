/**
 * Text-to-Speech module using Web Speech API.
 *
 * Pure functions — no React, no DOM dependencies.
 * Drop into any JS/TS project and call directly.
 */

export interface TTSOptions {
  lang?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
  voice?: string;
}

export type TTSVoice = {
  name: string;
  lang: string;
  isDefault: boolean;
};

/**
 * Check if Speech Synthesis is available in this browser.
 */
export function isSpeechSynthesisSupported(): boolean {
  if (typeof window === "undefined") return false;
  return "speechSynthesis" in window;
}

/**
 * Get available voices filtered by language.
 */
export function getVoices(lang?: string): TTSVoice[] {
  if (!isSpeechSynthesisSupported()) return [];
  const voices = window.speechSynthesis.getVoices();
  let filtered = voices;
  if (lang) {
    filtered = voices.filter((v) => v.lang.startsWith(lang));
  }
  return filtered.map((v) => ({
    name: v.name,
    lang: v.lang,
    isDefault: v.default,
  }));
}

/**
 * Speak text using the Web Speech API.
 *
 * Returns a promise that resolves when speaking completes.
 *
 * Usage:
 * ```ts
 * await speak("Hello, this is your interviewer.");
 * ```
 */
export function speak(
  text: string,
  options: TTSOptions = {}
): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!isSpeechSynthesisSupported()) {
      reject(new Error("Speech Synthesis is not supported in this browser."));
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options.lang ?? "en-US";
    utterance.rate = options.rate ?? 0.9;
    utterance.pitch = options.pitch ?? 1;
    utterance.volume = options.volume ?? 1;

    // Try to find a matching voice
    if (options.voice) {
      const voices = window.speechSynthesis.getVoices();
      const found = voices.find((v) => v.name === options.voice);
      if (found) utterance.voice = found;
    }

    utterance.onend = () => resolve();
    utterance.onerror = (event) => reject(event.error);

    window.speechSynthesis.speak(utterance);
  });
}

/**
 * Immediately stop any ongoing speech.
 */
export function stopSpeaking(): void {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
}
