"use client";

/**
 * PageTransition — Wraps content with fade/slide animations.
 *
 * Usage:
 *   import PageTransition from "@/components/page-transition";
 *
 *   export default function Page() {
 *     return (
 *       <PageTransition>
 *         <YourContent />
 *       </PageTransition>
 *     );
 *   }
 */

import { useEffect, useState, useRef, ReactNode } from "react";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

export default function PageTransition({ children, className = "" }: PageTransitionProps) {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Small delay to ensure DOM is ready before animating in
    const timer = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-500 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      } ${className}`}
    >
      {children}
    </div>
  );
}
