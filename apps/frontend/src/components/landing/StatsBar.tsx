"use client";

import { useStats } from "@/hooks/useStats";

function fmt(n: number): string {
  return n.toLocaleString("en-US");
}

export function StatsBar() {
  const { stats, loading } = useStats();

  const cells = [
    {
      label: "Documents Indexed",
      value: loading ? "—" : fmt(stats?.documents_indexed ?? 0),
      delta: loading ? "" : `+${fmt(stats?.docs_this_week ?? 0)} this week`,
      up: true,
    },
    {
      label: "Incident Reports",
      value: loading ? "—" : fmt(stats?.incident_docs ?? 0),
      delta: loading ? "" : "Postmortems · RCAs · Reports",
      up: true,
    },
    {
      label: "Knowledge Chunks",
      value: loading ? "—" : fmt(stats?.chunks_indexed ?? 0),
      delta: loading ? "" : "Semantic search units",
      up: true,
    },
    {
      label: "Uploads This Week",
      value: loading ? "—" : fmt(stats?.docs_this_week ?? 0),
      delta: loading ? "" : "Last 7 days",
      up: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-border rounded-xl overflow-hidden border border-border">
      {cells.map(({ label, value, delta, up }) => (
        <div key={label} className="bg-surface p-6 text-center space-y-1">
          <p className="text-2xl font-bold text-foreground tracking-tight">{value}</p>
          <p className="text-xs text-foreground-3">{label}</p>
          {delta && (
            <p className={`text-xs font-medium ${up ? "text-success" : "text-destructive"}`}>
              {delta}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
