export type DocumentType =
  | "incident_report"
  | "rca"
  | "runbook"
  | "postmortem"
  | "architecture"
  | "troubleshooting_guide"
  | "service_documentation";

export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export type Severity = "critical" | "high" | "medium" | "low" | "unknown";

export type ProcessingStage =
  | "uploading"
  | "extracting"
  | "chunking"
  | "enriching"
  | "embedding"
  | "indexing"
  | "completed"
  | "failed";

export interface Document {
  id: string;
  title: string;
  document_type: DocumentType;
  filename: string;
  file_size: number;
  status: DocumentStatus;
  chunk_count: number;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
  error_message?: string;
  stream_url?: string;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  skip: number;
  limit: number;
}

export interface ProcessingEvent {
  stage: ProcessingStage;
  message: string;
  progress: number;
  chunk_count?: number;
  error?: string;
}

export interface IncidentResult {
  document_id: string;
  title: string;
  document_type: DocumentType;
  relevance_score: number;
  excerpt: string;
  root_cause?: string;
  resolution?: string;
  affected_services: string[];
  severity: Severity;
}

export interface SearchResponse {
  query: string;
  ai_answer?: string;
  results: IncidentResult[];
  total_results: number;
  search_latency_ms: number;
}

export interface SimilarIncidentResult {
  document_id: string;
  title: string;
  similarity_score: number;
  shared_services: string[];
  resolution_summary?: string;
}

export interface SimilarIncidentsResponse {
  similar_incidents: SimilarIncidentResult[];
  total: number;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface SourceReference {
  document_id: string;
  title: string;
  excerpt: string;
  relevance_score: number;
}

export interface PlatformStats {
  documents_indexed: number;
  docs_this_week: number;
  incident_docs: number;
  chunks_indexed: number;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  sources: SourceReference[];
  suggested_runbooks: SourceReference[];
}
