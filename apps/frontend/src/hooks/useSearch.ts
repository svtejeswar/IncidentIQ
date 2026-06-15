"use client";

import { useState } from "react";
import { api } from "@/services/api";
import type { SearchResponse } from "@/types";

export function useSearch() {
  const [data, setData] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (query: string) => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.search.query({
        query,
        limit: 5,
        include_ai_answer: true,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
  };

  return { data, isLoading, error, search, reset };
}
