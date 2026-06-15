"use client";

import { useTheme } from "next-themes";
import { useEffect, useRef, useState } from "react";
import { Moon, Sun, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const themes = [
  {
    id: "dark",
    label: "Dark",
    icon: Moon,
    swatch: "bg-[#151519] border-[#2c2c3c]",
    dot: "bg-[#6366f1]",
  },
  {
    id: "light",
    label: "Light",
    icon: Sun,
    swatch: "bg-[#f8f9fb] border-[#cccedc]",
    dot: "bg-[#6366f1]",
  },
] as const;

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!open) return;
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  if (!mounted) return <div className="w-7 h-7" />;

  const current = themes.find((t) => t.id === resolvedTheme) ?? themes[0];
  const CurrentIcon = current.icon;

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "w-7 h-7 rounded-lg flex items-center justify-center transition-colors",
          "text-foreground-2 hover:text-foreground hover:bg-surface-2"
        )}
        aria-label="Toggle theme"
      >
        <CurrentIcon size={14} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 w-36 rounded-xl border border-border bg-surface shadow-lg shadow-black/20 py-1 z-50">
          {themes.map(({ id, label, icon: Icon, swatch, dot }) => {
            const active = (theme ?? resolvedTheme) === id;
            return (
              <button
                key={id}
                onClick={() => { setTheme(id); setOpen(false); }}
                className={cn(
                  "w-full flex items-center gap-2.5 px-3 py-2 text-left transition-colors",
                  active
                    ? "text-foreground"
                    : "text-foreground-2 hover:text-foreground hover:bg-surface-2"
                )}
              >
                <span
                  className={cn(
                    "w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0",
                    swatch
                  )}
                >
                  <span className={cn("w-2 h-2 rounded-full", dot)} />
                </span>
                <span className="text-xs flex-1">{label}</span>
                {active && <Check size={11} className="text-primary flex-shrink-0" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
