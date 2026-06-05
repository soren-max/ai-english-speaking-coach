"use client";

/** AnimatedScore — Counting number animation for scores */
import { useEffect, useState, useRef } from "react";

interface AnimatedScoreProps {
  value: number;
  max?: number;
  duration?: number;
  className?: string;
}

export default function AnimatedScore({
  value,
  max = 100,
  duration = 1000,
  className = "",
}: AnimatedScoreProps) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef<number | null>(null);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (value === 0) { setDisplay(0); return; }
    startRef.current = null;
    const step = (timestamp: number) => {
      if (startRef.current === null) startRef.current = timestamp;
      const progress = Math.min((timestamp - startRef.current) / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * value));
      if (progress < 1) rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [value, duration]);

  return (
    <span className={`tabular-nums ${className}`}>
      {display}<span className="text-sm text-muted-foreground">/{max}</span>
    </span>
  );
}
