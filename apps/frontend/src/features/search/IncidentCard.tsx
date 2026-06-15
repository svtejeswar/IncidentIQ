import { FileText, Wrench, AlertCircle, Server } from "lucide-react";
import type { IncidentResult } from "@/types";
import { formatDocumentType, severityColor } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface Props {
  result: IncidentResult;
  rank: number;
}

export function IncidentCard({ result, rank }: Props) {
  return (
    <div className="p-5 rounded-xl border border-border bg-surface hover:border-border-2 transition-colors space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <span className="text-xs text-foreground-3 font-mono mt-0.5 flex-shrink-0">
            {String(rank).padStart(2, "0")}
          </span>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-foreground leading-snug truncate">
              {result.title}
            </h3>
            <span className="text-xs text-foreground-3">
              {formatDocumentType(result.document_type)}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Badge className={severityColor(result.severity)}>{result.severity}</Badge>
          <span className="text-xs text-foreground-3 tabular-nums">
            {Math.round(result.relevance_score * 100)}%
          </span>
        </div>
      </div>

      <p className="text-sm text-foreground-2 leading-relaxed">{result.excerpt}</p>

      {(result.root_cause || result.resolution) && (
        <div className="grid gap-2">
          {result.root_cause && (
            <div className="flex items-start gap-2 text-xs">
              <AlertCircle size={12} className="text-orange mt-0.5 flex-shrink-0" />
              <span className="text-foreground-2">
                <span className="text-foreground-3">Root cause: </span>
                {result.root_cause}
              </span>
            </div>
          )}
          {result.resolution && (
            <div className="flex items-start gap-2 text-xs">
              <Wrench size={12} className="text-success mt-0.5 flex-shrink-0" />
              <span className="text-foreground-2">
                <span className="text-foreground-3">Resolution: </span>
                {result.resolution}
              </span>
            </div>
          )}
        </div>
      )}

      {result.affected_services.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {result.affected_services.map((svc) => (
            <span
              key={svc}
              className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-md bg-surface-2 border border-border text-foreground-2"
            >
              <Server size={10} />
              {svc}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
