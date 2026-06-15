"use client";

import { useState } from "react";
import { api } from "@/services/api";
import type { Document, DocumentType } from "@/types";

interface UploadState {
  document: Document | null;
  isUploading: boolean;
  error: string | null;
}

export function useUpload() {
  const [state, setState] = useState<UploadState>({
    document: null,
    isUploading: false,
    error: null,
  });

  const upload = async (
    file: File,
    documentType: DocumentType,
    title?: string
  ) => {
    setState({ document: null, isUploading: true, error: null });
    try {
      const document = await api.documents.upload(file, documentType, title);
      setState({ document, isUploading: false, error: null });
      return document;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setState({ document: null, isUploading: false, error: message });
      return null;
    }
  };

  const reset = () =>
    setState({ document: null, isUploading: false, error: null });

  return { ...state, upload, reset };
}
