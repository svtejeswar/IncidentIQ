import { Upload } from "lucide-react";
import { UploadForm } from "@/features/upload/UploadForm";

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      <div className="space-y-1">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center">
            <Upload size={15} className="text-primary" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">Upload Document</h1>
        </div>
        <p className="text-sm text-foreground-2 pl-[2.625rem]">
          Add incident reports, RCAs, runbooks, or architecture docs to your knowledge base.
        </p>
      </div>

      <div className="p-6 rounded-xl border border-border bg-surface">
        <UploadForm />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded-lg border border-border bg-surface space-y-1">
          <p className="text-sm font-medium text-foreground">Supported formats</p>
          <p className="text-xs text-foreground-2">PDF, DOCX, TXT, Markdown</p>
        </div>
        <div className="p-4 rounded-lg border border-border bg-surface space-y-1">
          <p className="text-sm font-medium text-foreground">Max file size</p>
          <p className="text-xs text-foreground-2">50 MB per document</p>
        </div>
      </div>
    </div>
  );
}
