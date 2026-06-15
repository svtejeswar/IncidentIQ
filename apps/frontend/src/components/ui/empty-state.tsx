import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 gap-4 text-center", className)}>
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-surface-2 border border-border flex items-center justify-center">
          <Icon size={20} className="text-foreground-3" />
        </div>
      )}
      <div className="space-y-1">
        <p className="text-sm font-medium text-foreground">{title}</p>
        {description && (
          <p className="text-sm text-foreground-2 max-w-xs">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}
