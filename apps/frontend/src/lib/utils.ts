import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateStr));
}

export function formatDocumentType(type: string): string {
  return type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function severityColor(severity: string): string {
  const map: Record<string, string> = {
    critical: "text-destructive bg-destructive-dim",
    high: "text-orange bg-orange-dim",
    medium: "text-warning bg-warning-dim",
    low: "text-primary bg-primary-dim",
    unknown: "text-foreground-2 bg-surface-2",
  };
  return map[severity] ?? map["unknown"];
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    pending: "text-warning bg-warning-dim",
    processing: "text-primary bg-primary-dim",
    completed: "text-success bg-success-dim",
    failed: "text-destructive bg-destructive-dim",
  };
  return map[status] ?? "text-foreground-2 bg-surface-2";
}
