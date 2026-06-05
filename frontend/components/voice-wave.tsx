"use client";

/** Voice wave animation — shows when TTS is speaking */
import { useEffect, useRef } from "react";

interface VoiceWaveProps {
  isActive: boolean;
  size?: "sm" | "md";
}

export default function VoiceWave({ isActive, size = "sm" }: VoiceWaveProps) {
  const barCount = size === "sm" ? 3 : 5;
  const bars = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    if (!isActive) return;
    bars.current.forEach((bar, i) => {
      if (!bar) return;
      const h = 4 + Math.random() * 12;
      bar.style.height = `${h}px`;
    });
    const interval = setInterval(() => {
      bars.current.forEach((bar) => {
        if (!bar) return;
        bar.style.height = `${4 + Math.random() * 12}px`;
      });
    }, 200);
    return () => clearInterval(interval);
  }, [isActive]);

  if (!isActive) return null;

  return (
    <div className="flex items-end gap-0.5 h-4 px-1">
      {Array.from({ length: barCount }).map((_, i) => (
        <div
          key={i}
          ref={(el) => { if (el) bars.current[i] = el; }}
          className="w-1 bg-primary rounded-full transition-all duration-150"
          style={{ height: "4px" }}
        />
      ))}
    </div>
  );
}
