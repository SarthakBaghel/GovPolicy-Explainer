import { cn } from "@/lib/utils";

interface LoaderProps {
  className?: string;
  label?: string;
}

export function Loader({ className, label = "Loading" }: LoaderProps) {
  return (
    <div className={cn("inline-flex items-center gap-2 text-sm text-muted", className)}>
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary/30 border-t-primary" />
      <span>{label}...</span>
    </div>
  );
}
