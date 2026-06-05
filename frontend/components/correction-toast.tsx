"use client";

/** CorrectionToast — popup showing real-time expression correction */
import { useEffect, useState } from "react";
import { X, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { speak } from "@/voice/text-to-speech";

interface CorrectionToastProps {
  original?: string;
  corrected?: string;
  explanation?: string;
  ttsText?: string;
  visible: boolean;
  onDismiss: () => void;
}

export default function CorrectionToast({
  original,
  corrected,
  explanation,
  ttsText,
  visible,
  onDismiss,
}: CorrectionToastProps) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (visible) {
      setShow(true);
      // Auto-dismiss after 8s
      const timer = setTimeout(() => { setShow(false); onDismiss(); }, 8000);
      return () => clearTimeout(timer);
    } else {
      setShow(false);
    }
  }, [visible, onDismiss]);

  if (!show || !original) return null;

  return (
    <div className="fixed bottom-28 left-1/2 -translate-x-1/2 z-50 w-full max-w-md animate-in slide-in-from-bottom fade-in duration-300">
      <div className="bg-card border border-green-200 dark:border-green-900 rounded-xl shadow-2xl p-4 mx-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide">
            💡 Try saying it like this
          </span>
          <Button variant="ghost" size="icon" className="w-5 h-5 -mt-1 -mr-1" onClick={() => { setShow(false); onDismiss(); }}>
            <X className="w-3 h-3" />
          </Button>
        </div>

        <div className="space-y-1.5 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-red-500 font-medium shrink-0">Before:</span>
            <span className="line-through text-muted-foreground">{original}</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-500 font-medium shrink-0">After:</span>
            <span className="font-medium text-foreground">{corrected}</span>
          </div>
          {explanation && (
            <p className="text-xs text-muted-foreground mt-1 italic">{explanation}</p>
          )}
        </div>

        {ttsText && (
          <Button
            variant="outline"
            size="sm"
            className="mt-2 w-full text-xs"
            onClick={() => speak(ttsText)}
          >
            <Volume2 className="w-3 h-3 mr-1.5" />
            Play correction
          </Button>
        )}
      </div>
    </div>
  );
}
