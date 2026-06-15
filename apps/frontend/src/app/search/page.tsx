"use client";

import { Search } from "lucide-react";
import { SearchBar } from "@/features/search/SearchBar";
import { SearchResults } from "@/features/search/SearchResults";
import { Spinner } from "@/components/ui/spinner";
import { useSearch } from "@/hooks/useSearch";

export default function SearchPage() {
  const { data, isLoading, error, search } = useSearch();

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      <div className="space-y-1">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center">
            <Search size={15} className="text-primary" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">Search Incidents</h1>
        </div>
        <p className="text-sm text-foreground-2 pl-[2.625rem]">
          Search your operational knowledge base using natural language.
        </p>
      </div>

      <SearchBar onSearch={search} isLoading={isLoading} />

      {error && (
        <div className="p-4 rounded-lg bg-destructive-dim border border-destructive/20 text-destructive text-sm">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="flex flex-col items-center py-16 gap-3 text-foreground-2">
          <Spinner size={20} />
          <p className="text-sm">Searching knowledge base…</p>
        </div>
      )}

      {data && !isLoading && <SearchResults response={data} />}
    </div>
  );
}
