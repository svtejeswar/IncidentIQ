"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { useUpload } from "@/hooks/useUpload";
import { useSSE } from "@/hooks/useSSE";
import { ProcessingProgress } from "./ProcessingProgress";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";
import type { DocumentType } from "@/types";

const DOCUMENT_TYPES: { value: DocumentType; label: string }[] = [
  { value: "incident_report", label: "Incident Report" },
  { value: "rca", label: "Root Cause Analysis (RCA)" },
  { value: "runbook", label: "Runbook" },
  { value: "postmortem", label: "Postmortem" },
  { value: "architecture", label: "Architecture Document" },
  { value: "troubleshooting_guide", label: "Troubleshooting Guide" },
  { value: "service_documentation", label: "Service Documentation" },
];

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType>("incident_report");
  const [title, setTitle] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { document, isUploading, error, upload, reset } = useUpload();
  const { lastEvent, isCompleted, isFailed } = useSSE(document?.stream_url ?? null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    await upload(file, documentType, title || undefined);
  };

  if (document) {
    return (
      <div className="space-y-6">
        <ProcessingProgress
          document={document}
          lastEvent={lastEvent}
          isCompleted={isCompleted}
          isFailed={isFailed}
        />
        {(isCompleted || isFailed) && (
          <button
            onClick={reset}
            className="text-sm text-foreground-2 hover:text-foreground border border-border hover:border-border-2 px-4 py-2 rounded-lg transition-colors"
          >
            Upload another document
          </button>
        )}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors",
          isDragOver
            ? "border-primary bg-primary-dim"
            : "border-border hover:border-border-2 hover:bg-surface-2"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />

        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileText size={18} className="text-primary flex-shrink-0" />
            <div className="text-left">
              <p className="text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-foreground-2">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              className="ml-2 text-foreground-3 hover:text-foreground-2 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border flex items-center justify-center mx-auto">
              <UploadCloud size={18} className="text-foreground-3" />
            </div>
            <div>
              <p className="text-sm text-foreground">Drop a file or click to browse</p>
              <p className="text-xs text-foreground-3 mt-0.5">PDF, DOCX, TXT, MD — up to 50 MB</p>
            </div>
          </div>
        )}
      </div>

      {/* Document type */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-foreground-2">Document Type</label>
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value as DocumentType)}
          className="w-full px-3 py-2.5 bg-surface-2 border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-colors"
        >
          {DOCUMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      {/* Title */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-foreground-2">
          Title <span className="text-foreground-3">(optional)</span>
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Payment Service Outage — March 2024"
          className="w-full px-3 py-2.5 bg-surface-2 border border-border rounded-lg text-sm text-foreground placeholder-foreground-3 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-colors"
        />
      </div>

      {error && (
        <p className="text-destructive text-sm border border-destructive/20 bg-destructive-dim rounded-lg px-4 py-3">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={!file || isUploading}
        className="w-full py-2.5 flex items-center justify-center gap-2 bg-primary hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed text-primary-fg text-sm font-medium rounded-lg transition-opacity"
      >
        {isUploading ? (
          <>
            <Spinner size={14} className="text-primary-fg" />
            Uploading…
          </>
        ) : (
          <>
            <UploadCloud size={14} />
            Upload &amp; Process
          </>
        )}
      </button>
    </form>
  );
}
