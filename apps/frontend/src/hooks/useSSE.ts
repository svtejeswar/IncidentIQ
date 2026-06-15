"use client";

import { useEffect, useRef, useState } from "react";
import type { ProcessingEvent } from "@/types";

interface UseSSEResult {
  events: ProcessingEvent[];
  lastEvent: ProcessingEvent | null;
  isConnected: boolean;
  isCompleted: boolean;
  isFailed: boolean;
}

export function useSSE(url: string | null): UseSSEResult {
  const [events, setEvents] = useState<ProcessingEvent[]>([]);
  const [lastEvent, setLastEvent] = useState<ProcessingEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!url) return;

    const fullUrl = url.startsWith("http")
      ? url
      : `${process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") ?? "http://localhost:8000"}${url}`;

    const source = new EventSource(fullUrl);
    sourceRef.current = source;

    source.onopen = () => setIsConnected(true);

    source.onmessage = (e) => {
      try {
        const event: ProcessingEvent = JSON.parse(e.data);
        setLastEvent(event);
        setEvents((prev) => [...prev, event]);

        if (event.stage === "completed" || event.stage === "failed") {
          source.close();
          setIsConnected(false);
        }
      } catch {
        // ignore malformed events
      }
    };

    source.onerror = () => {
      setIsConnected(false);
      source.close();
    };

    return () => {
      source.close();
      setIsConnected(false);
    };
  }, [url]);

  const isCompleted = lastEvent?.stage === "completed";
  const isFailed = lastEvent?.stage === "failed";

  return { events, lastEvent, isConnected, isCompleted, isFailed };
}
