"use client";

import { CheckCircle2, XCircle, Loader2, Circle } from "lucide-react";
import type { Document, ProcessingEvent } from "@/types";
import { cn } from "@/lib/utils";

const STAGES = [
  { key: "extracting", label: "Extracting text" },
  { key: "chunking", label: "Chunking content" },
  { key: "enriching", label: "Enriching metadata" },
  { key: "embedding", label: "Generating embeddings" },
  { key: "indexing", label: "Indexing vectors" },
  { key: "completed", label: "Complete" },
];

interface Props {
  document: Document;
  lastEvent: ProcessingEvent | null;
  isCompleted: boolean;
  isFailed: boolean;
}

export function ProcessingProgress({ document, lastEvent, isCompleted, isFailed }: Props) {
  const currentStage = lastEvent?.stage ?? "extracting";
  const progress = lastEvent?.progress ?? 5;
  const currentIndex = STAGES.findIndex((s) => s.key === currentStage);

  return (
    <div className="space-y-5">
      {/* Header card */}
      <div className="p-5 rounded-xl border border-border bg-surface-2 space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-foreground truncate">{document.title}</h3>
            <p className="text-xs text-foreground-2 mt-0.5">{document.filename}</p>
          </div>
          <span
            className={cn(
              "text-xs px-2.5 py-1 rounded-full font-medium flex-shrink-0",
              isCompleted
                ? "text-success bg-success-dim"
                : isFailed
                ? "text-destructive bg-destructive-dim"
                : "text-primary bg-primary-dim"
            )}
          >
            {isCompleted ? "Completed" : isFailed ? "Failed" : "Processing"}
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-surface rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-700 ease-out",
              isFailed ? "bg-destructive" : "bg-primary"
            )}
            style={{ width: `${progress}%` }}
          />
        </div>

        {lastEvent?.message && (
          <p className="text-xs text-foreground-2">{lastEvent.message}</p>
        )}
      </div>

      {/* Stage checklist */}
      <div className="space-y-1">
        {STAGES.map((stage, stageIndex) => {
          const isDone = stageIndex < currentIndex || (isCompleted && stage.key === "completed");
          const isCurrent = stage.key === currentStage && !isCompleted && !isFailed;

          return (
            <div
              key={stage.key}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isCurrent ? "bg-primary-dim" : ""
              )}
            >
              {isDone ? (
                <CheckCircle2 size={15} className="text-success flex-shrink-0" />
              ) : isFailed && stage.key === currentStage ? (
                <XCircle size={15} className="text-destructive flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 size={15} className="text-primary animate-spin flex-shrink-0" />
              ) : (
                <Circle size={15} className="text-foreground-3 flex-shrink-0" />
              )}
              <span
                className={cn(
                  isDone
                    ? "text-success"
                    : isCurrent
                    ? "text-primary font-medium"
                    : "text-foreground-3"
                )}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>

      {isCompleted && lastEvent?.chunk_count && (
        <div className="p-4 rounded-lg bg-success-dim border border-success/20 text-success text-sm flex items-center gap-2">
          <CheckCircle2 size={14} />
          {lastEvent.chunk_count} chunks indexed and ready for search.
        </div>
      )}
    </div>
  );
}
