"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";

const navLinks = [
  { href: "/#features", label: "Features" },
  { href: "/#how-it-works", label: "How it works" },
];

export function Navbar() {
  const pathname = usePathname();
  const isApp = pathname !== "/";

  return (
    <nav className="sticky top-0 z-50 h-14 bg-surface border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-primary flex items-center justify-center">
              <Zap size={12} className="text-white" strokeWidth={2.5} />
            </div>
            <span className="text-sm font-semibold text-foreground tracking-tight">
              IncidentIQ
            </span>
          </Link>

          {!isApp && (
            <div className="hidden md:flex items-center gap-6">
              {navLinks.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className="text-xs text-foreground-2 hover:text-foreground transition-colors"
                >
                  {label}
                </Link>
              ))}
            </div>
          )}

          {isApp && (
            <div className="hidden md:flex items-center gap-1">
              {[
                { href: "/upload", label: "Upload" },
                { href: "/search", label: "Search" },
                { href: "/assistant", label: "Assistant" },
              ].map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                    pathname === href
                      ? "bg-primary-dim text-primary"
                      : "text-foreground-2 hover:text-foreground hover:bg-surface-2"
                  )}
                >
                  {label}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <div className="w-px h-4 bg-border mx-1" />
          {!isApp ? (
            <>
              <Link
                href="/search"
                className="text-xs text-foreground-2 hover:text-foreground transition-colors"
              >
                Search
              </Link>
              <Link
                href="/upload"
                className="px-3 py-1.5 bg-primary text-primary-fg text-xs font-medium rounded-lg hover:opacity-90 transition-opacity"
              >
                Upload docs
              </Link>
            </>
          ) : (
            <Link
              href="/"
              className="text-xs text-foreground-2 hover:text-foreground transition-colors"
            >
              ← Home
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
