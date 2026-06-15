import { MessageSquare } from "lucide-react";
import { ChatInterface } from "@/features/assistant/ChatInterface";

export default function AssistantPage() {
  return (
    <div className="flex flex-col px-4 sm:px-6 py-6" style={{ height: "calc(100vh - 3.5rem)" }}>
      <div className="space-y-1 flex-shrink-0 mb-5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary-dim flex items-center justify-center">
            <MessageSquare size={15} className="text-primary" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">AI Assistant</h1>
        </div>
        <p className="text-sm text-foreground-2 pl-[2.625rem]">
          Chat with your operational knowledge base. Grounded in your uploaded documents.
        </p>
      </div>

      <div className="flex-1 min-h-0 max-w-3xl w-full mx-auto rounded-xl border border-border bg-surface overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
