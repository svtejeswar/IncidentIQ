"use client";

import { useState } from "react";
import { Search, ArrowRight } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";

interface Props {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "Database connection timeouts",
  "Authentication service outage",
  "Redis cache failure recovery",
  "SQS message backlog",
];

export function SearchBar({ onSearch, isLoading }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <Search
            size={14}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-foreground-3 pointer-events-none"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about any incident, root cause, or service failure…"
            className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-sm text-foreground placeholder-foreground-3 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed text-primary-fg text-sm font-medium rounded-lg transition-opacity"
        >
          {isLoading ? <Spinner size={14} className="text-primary-fg" /> : <ArrowRight size={14} />}
          {isLoading ? "Searching" : "Search"}
        </button>
      </form>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-foreground-3">Try:</span>
        {EXAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            onClick={() => { setQuery(q); onSearch(q); }}
            className="text-xs px-2.5 py-1 rounded-md border border-border text-foreground-2 hover:text-foreground hover:border-border-2 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
