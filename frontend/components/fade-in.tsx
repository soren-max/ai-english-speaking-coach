"use client";

/**
 * FadeIn — Staggered fade-in animation for lists/cards.
 *
 * Usage:
 *   import FadeIn from "@/components/fade-in";
 *
 *   {items.map((item, i) => (
 *     <FadeIn key={i} delay={i * 100}>
 *       <Card>{item}</Card>
 *     </FadeIn>
 *   ))}
 */

import { useEffect, useState, ReactNode } from "react";

interface FadeInProps {
  children: ReactNode;
  delay?: number;       // ms delay before animating
  className?: string;
}

export default function FadeIn({ children, delay = 0, className = "" }: FadeInProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      className={`transition-all duration-500 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
      } ${className}`}
    >
      {children}
    </div>
  );
}
