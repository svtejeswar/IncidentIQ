import { Zap, Search } from "lucide-react";
import type { SearchResponse } from "@/types";
import { IncidentCard } from "./IncidentCard";
import { EmptyState } from "@/components/ui/empty-state";

interface Props {
  response: SearchResponse;
}

export function SearchResults({ response }: Props) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-xs text-foreground-3">
        <span>{response.total_results} result{response.total_results !== 1 ? "s" : ""}</span>
        <span>·</span>
        <span className="text-foreground-2">"{response.query}"</span>
        <span>·</span>
        <span>{response.search_latency_ms}ms</span>
      </div>

      {/* AI Answer */}
      {response.ai_answer && (
        <div className="p-5 rounded-xl border border-primary/20 bg-primary-dim space-y-2">
          <div className="flex items-center gap-2">
            <Zap size={13} className="text-primary" />
            <span className="text-xs font-semibold text-primary uppercase tracking-wide">AI Answer</span>
          </div>
          <p className="text-sm text-foreground leading-relaxed">{response.ai_answer}</p>
        </div>
      )}

      {/* Results */}
      {response.results.length === 0 ? (
        <EmptyState
          icon={Search}
          title="No results found"
          description="Try rephrasing your query or uploading more incident documents."
        />
      ) : (
        <div className="space-y-3">
          {response.results.map((result, i) => (
            <IncidentCard key={result.document_id} result={result} rank={i + 1} />
          ))}
        </div>
      )}
    </div>
  );
}
