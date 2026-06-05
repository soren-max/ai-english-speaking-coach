/**
 * Speech-to-Text module using Web Speech API.
 *
 * Pure functions — no React, no DOM dependencies.
 * Drop into any JS/TS project and call directly.
 */

export interface STTOptions {
  lang?: string;
  continuous?: boolean;
  interimResults?: boolean;
}

export interface STTResult {
  text: string;
  isFinal: boolean;
}

type STTCallback = (result: STTResult) => void;
type STTErrorCallback = (error: string) => void;

/**
 * Check if Speech Recognition is available in this browser.
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === "undefined") return false;
  return !!(
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  );
}

/**
 * Create a speech recognition instance.
 *
 * Usage:
 * ```ts
 * const stt = createSpeechRecognizer({
 *   onResult: (r) => console.log(r.text),
 *   onError: (e) => console.error(e),
 * });
 * stt.start();
 * // ... later
 * stt.stop();
 * ```
 */
export function createSpeechRecognizer(
  callbacks: {
    onResult: STTCallback;
    onError?: STTErrorCallback;
    onEnd?: () => void;
  },
  options: STTOptions = {}
) {
  if (!isSpeechRecognitionSupported()) {
    throw new Error("Speech Recognition is not supported in this browser.");
  }

  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.lang = options.lang ?? "en-US";
  recognition.continuous = options.continuous ?? false;
  recognition.interimResults = options.interimResults ?? false;

  recognition.onresult = (event: SpeechRecognitionEvent) => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const isFinal = event.results[i].isFinal;
      const text = event.results[i][0].transcript;
      callbacks.onResult({ text, isFinal });
    }
  };

  recognition.onerror = (event: any) => {
    callbacks.onError?.(event.error ?? "Unknown error");
  };

  recognition.onend = () => {
    callbacks.onEnd?.();
  };

  return {
    start: () => recognition.start(),
    stop: () => recognition.stop(),
    abort: () => recognition.abort(),
  };
}
