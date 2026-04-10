import { cn } from "@/lib/utils";

interface BadgeProps {
  label: string;
  intent?: "default" | "success" | "warning";
}

export function Badge({ label, intent = "default" }: BadgeProps) {
  const styles = {
    default: "bg-slate-100 text-slate-700",
    success: "bg-green-100 text-green-800",
    warning: "bg-amber-100 text-amber-800",
  };

  return <span className={cn("rounded-full px-2.5 py-1 text-xs font-medium", styles[intent])}>{label}</span>;
}
