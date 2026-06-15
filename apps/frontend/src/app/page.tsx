import Link from "next/link";
import {
  ArrowRight,
  FileText,
  Search,
  MessageSquare,
  Zap,
  GitBranch,
  Database,
  TrendingUp,
  ChevronRight,
} from "lucide-react";
import { StatsBar } from "@/components/landing/StatsBar";

const pipelineSteps = [
  { label: "Documents", sub: "PDFs, runbooks, docs", icon: FileText },
  { label: "Embeddings", sub: "Vector representations", icon: Database },
  { label: "Vector Search", sub: "Semantic retrieval", icon: Search },
  { label: "AI Answer", sub: "Grounded responses", icon: MessageSquare },
];

const features = [
  {
    icon: FileText,
    title: "Document Ingestion",
    desc: "Drop in PDFs, DOCX, Markdown, and plain text. We chunk, embed, and index automatically.",
  },
  {
    icon: Search,
    title: "Semantic Search",
    desc: "Find incidents by meaning, not keywords. Surface relevant incidents across thousands of documents.",
  },
  {
    icon: MessageSquare,
    title: "AI Assistant",
    desc: "Ask questions in plain English and get grounded answers with citations to source documents.",
  },
  {
    icon: GitBranch,
    title: "Similar Incident Discovery",
    desc: "Automatically link new incidents to historical ones using vector similarity.",
  },
  {
    icon: TrendingUp,
    title: "Root Cause Analysis",
    desc: "Extract patterns across postmortems to identify recurring failure modes.",
  },
  {
    icon: Database,
    title: "Operational Knowledge Hub",
    desc: "A single searchable home for runbooks, architecture docs, and tribal knowledge.",
  },
];

const archSteps = [
  { n: "1", label: "Upload", sub: "Ingest any format" },
  { n: "2", label: "Chunk", sub: "Segment content" },
  { n: "3", label: "Embed", sub: "Semantic vectors" },
  { n: "4", label: "Search", sub: "Retrieve top-k" },
  { n: "5", label: "LLM", sub: "Reason over context" },
  { n: "6", label: "Answer", sub: "Cited response" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="pt-20 pb-16 px-4 text-center relative overflow-hidden">
        {/* subtle radial glow */}
        <div
          className="absolute inset-x-0 top-0 h-96 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 70% 40% at 50% 0%, rgba(99,102,241,0.12), transparent)",
          }}
        />

        <div className="relative max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-surface text-foreground-2 text-xs">
            <Zap size={10} className="text-primary" />
            AI-powered incident intelligence
            <span className="text-foreground-3">· Next-generation platform</span>
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight text-foreground">
            Learn From Every Incident
          </h1>
          <p className="text-base text-foreground-2 max-w-xl mx-auto leading-relaxed">
            Transform incident reports, runbooks, and operational documents into a
            searchable AI-powered knowledge platform.
          </p>

          <div className="flex items-center justify-center gap-3 pt-2">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-fg text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              <FileText size={14} />
              Upload Documents
            </Link>
            <Link
              href="/search"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-border text-foreground-2 hover:text-foreground hover:bg-surface-2 text-sm font-medium rounded-lg transition-colors"
            >
              Explore Knowledge Base
              <ChevronRight size={14} />
            </Link>
          </div>
        </div>

        {/* Pipeline visualization */}
        <div className="relative max-w-2xl mx-auto mt-14">
          <div className="text-left mb-3">
            <p className="text-xs font-semibold text-foreground-3 uppercase tracking-widest">
              The Retrieval Pipeline
            </p>
            <p className="text-xs text-foreground-3">
              From raw documents to grounded answers
            </p>
          </div>
          <div className="flex items-center gap-0 p-4 rounded-xl border border-border bg-surface">
            {pipelineSteps.map(({ label, sub, icon: Icon }, i) => (
              <div key={label} className="flex items-center flex-1 min-w-0">
                <div className="flex-1 min-w-0 p-3 rounded-lg border border-border bg-surface-2 text-left">
                  <div className="w-6 h-6 rounded-md bg-primary-dim flex items-center justify-center mb-2">
                    <Icon size={11} className="text-primary" />
                  </div>
                  <p className="text-xs font-medium text-foreground truncate">{label}</p>
                  <p className="text-xs text-foreground-3 truncate mt-0.5">{sub}</p>
                </div>
                {i < pipelineSteps.length - 1 && (
                  <ChevronRight size={14} className="text-foreground-3 flex-shrink-0 mx-1" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="px-4 pb-16">
        <div className="max-w-5xl mx-auto">
          <StatsBar />
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-4 py-20 bg-surface border-y border-border">
        <div className="max-w-5xl mx-auto space-y-12">
          <div className="max-w-xl space-y-3">
            <h2 className="text-3xl font-bold text-foreground leading-tight">
              Everything your team needs
              <br />
              to operationalize knowledge
            </h2>
            <p className="text-sm text-foreground-2 leading-relaxed">
              Built for engineers, SREs, and platform teams who want to turn every
              postmortem into durable, searchable intelligence.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="p-5 rounded-xl border border-border bg-background hover:border-border-2 transition-colors space-y-3"
              >
                <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center">
                  <Icon size={15} className="text-primary" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">{title}</p>
                  <p className="text-xs text-foreground-2 mt-1 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="how-it-works" className="px-4 py-20">
        <div className="max-w-5xl mx-auto space-y-10 text-center">
          <div className="space-y-2">
            <p className="text-xs text-foreground-3 uppercase tracking-widest">How it works</p>
            <h2 className="text-2xl font-bold text-foreground">
              A production-grade RAG architecture
            </h2>
            <p className="text-sm text-foreground-2 max-w-md mx-auto">
              Every document flows through the same reliable pipeline — from ingestion to a cited,
              trustworthy answer.
            </p>
          </div>

          <div className="flex items-start justify-center gap-2 flex-wrap">
            {archSteps.map(({ n, label, sub }, i) => (
              <div key={label} className="flex items-center gap-2">
                <div className="text-center space-y-2">
                  <div className="w-10 h-10 rounded-xl border border-border bg-surface flex items-center justify-center mx-auto text-foreground-3 font-mono text-xs font-semibold">
                    {n}
                  </div>
                  <p className="text-xs font-medium text-foreground w-16">{label}</p>
                  <p className="text-xs text-foreground-3 w-16 leading-tight">{sub}</p>
                </div>
                {i < archSteps.length - 1 && (
                  <ArrowRight size={13} className="text-foreground-3 flex-shrink-0 mb-8" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-4 py-20 bg-surface border-t border-border">
        <div className="max-w-3xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="space-y-1 text-center sm:text-left">
            <h2 className="text-2xl font-bold text-foreground">
              Stop relearning the same lessons
            </h2>
            <p className="text-sm text-foreground-2">
              Build your incident history today and give your team instant, grounded answers tomorrow.
            </p>
          </div>
          <div className="flex items-center gap-3 flex-shrink-0">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-fg text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              <FileText size={14} />
              Upload Documents
            </Link>
            <Link
              href="/assistant"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-border text-foreground-2 hover:text-foreground hover:bg-surface-2 text-sm font-medium rounded-lg transition-colors"
            >
              Try the AI Assistant
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-6 border-t border-border">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <p className="text-xs text-foreground-3">
            © 2025 IncidentIQ. Built for engineering teams.
          </p>
          <div className="flex items-center gap-4">
            {[
              { label: "Upload", href: "/upload" },
              { label: "Search", href: "/search" },
              { label: "Assistant", href: "/assistant" },
            ].map(({ label, href }) => (
              <Link key={href} href={href} className="text-xs text-foreground-3 hover:text-foreground-2 transition-colors">
                {label}
              </Link>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
