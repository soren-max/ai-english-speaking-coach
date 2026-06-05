"use client";

/** Theme switcher — multiple CSS variable themes for demo质感 */
import { useEffect, useState } from "react";
import { Palette } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const THEMES = [
  { name: "Default", primary: "hsl(222, 47%, 40%)" },
  { name: "Emerald", primary: "hsl(160, 84%, 39%)" },
  { name: "Violet", primary: "hsl(271, 81%, 56%)" },
  { name: "Rose", primary: "hsl(346, 77%, 50%)" },
  { name: "Amber", primary: "hsl(38, 92%, 50%)" },
];

export default function ThemeSwitcher() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const applyTheme = (primary: string) => {
    document.documentElement.style.setProperty("--primary", primary);
    localStorage.setItem("interviewgpt-theme", primary);
  };

  if (!mounted) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" title="Theme">
          <Palette className="w-4 h-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {THEMES.map((t) => (
          <DropdownMenuItem
            key={t.name}
            onClick={() => applyTheme(t.primary)}
            className="flex items-center gap-2"
          >
            <span
              className="w-4 h-4 rounded-full border"
              style={{ backgroundColor: t.primary }}
            />
            {t.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
