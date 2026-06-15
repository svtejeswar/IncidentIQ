"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";
import type { PlatformStats } from "@/types";

export function useStats() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.stats
      .get()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading };
}
