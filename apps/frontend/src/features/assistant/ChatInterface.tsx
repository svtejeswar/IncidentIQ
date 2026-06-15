"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Zap, FileText } from "lucide-react";
import { api } from "@/services/api";
import type { ChatMessage as ChatMessageType, SourceReference } from "@/types";
import { ChatMessage } from "./ChatMessage";
import { Spinner } from "@/components/ui/spinner";

const SUGGESTIONS = [
  "Have we seen login service failures before?",
  "What caused previous payment timeouts?",
  "Show me runbooks for Redis failures",
  "Which services commonly fail together?",
];

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [sources, setSources] = useState<SourceReference[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: ChatMessageType = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.assistant.chat({
        message: text,
        conversation_id: conversationId,
        history: messages.slice(-6),
      });

      setConversationId(response.conversation_id);
      setSources(response.sources);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-primary-dim flex items-center justify-center">
              <Zap size={20} className="text-primary" />
            </div>
            <div className="space-y-1.5">
              <h2 className="text-base font-semibold text-foreground">IncidentIQ Assistant</h2>
              <p className="text-sm text-foreground-2 max-w-sm">
                Ask me anything about your operational knowledge. I'll search through your
                incident history and provide contextual, grounded answers.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-xs px-3 py-1.5 rounded-lg border border-border text-foreground-2 hover:text-foreground hover:border-border-2 hover:bg-surface-2 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center flex-shrink-0 mt-1">
              <Zap size={12} className="text-white" strokeWidth={2.5} />
            </div>
            <div className="bg-surface-2 border border-border rounded-xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center">
                <span className="w-1.5 h-1.5 bg-foreground-3 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-foreground-3 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-foreground-3 rounded-full animate-bounce" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="border-t border-border px-5 py-3 space-y-2">
          <p className="text-xs text-foreground-3 font-medium">Sources</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {sources.map((src) => (
              <div
                key={src.document_id}
                title={src.title}
                className="flex items-center gap-1.5 flex-shrink-0 text-xs px-2.5 py-1.5 rounded-lg bg-surface-2 border border-border text-foreground-2 max-w-[180px]"
              >
                <FileText size={10} className="flex-shrink-0 text-foreground-3" />
                <span className="truncate">{src.title}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-border p-4">
        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about incidents, root causes, or runbooks…"
            className="flex-1 px-3 py-2.5 bg-surface-2 border border-border rounded-lg text-sm text-foreground placeholder-foreground-3 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-primary hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed text-primary-fg text-sm font-medium rounded-lg transition-opacity"
          >
            {isLoading ? <Spinner size={14} className="text-primary-fg" /> : <Send size={14} />}
          </button>
        </form>
      </div>
    </div>
  );
}
