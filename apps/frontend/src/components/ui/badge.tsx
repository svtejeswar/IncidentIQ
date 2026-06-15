import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "primary" | "success" | "warning" | "destructive" | "orange";

const variants: Record<BadgeVariant, string> = {
  default: "bg-surface-2 text-foreground-2",
  primary: "bg-primary-dim text-primary",
  success: "bg-success-dim text-success",
  warning: "bg-warning-dim text-warning",
  destructive: "bg-destructive-dim text-destructive",
  orange: "bg-orange-dim text-orange",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
