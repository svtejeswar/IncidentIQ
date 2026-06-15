import { Zap, User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/types";
import { cn } from "@/lib/utils";

interface Props {
  message: ChatMessageType;
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center flex-shrink-0 mt-1">
          <Zap size={12} className="text-white" strokeWidth={2.5} />
        </div>
      )}
      <div
        className={cn(
          "max-w-[75%] rounded-xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "bg-primary text-primary-fg rounded-tr-sm"
            : "bg-surface-2 border border-border text-foreground rounded-tl-sm"
        )}
      >
        {message.content}
      </div>
      {isUser && (
        <div className="w-7 h-7 rounded-lg bg-surface-2 border border-border flex items-center justify-center flex-shrink-0 mt-1">
          <User size={12} className="text-foreground-2" />
        </div>
      )}
    </div>
  );
}
