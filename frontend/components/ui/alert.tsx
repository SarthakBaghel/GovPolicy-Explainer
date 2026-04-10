import { cn } from "@/lib/utils";

type AlertVariant = "info" | "success" | "error";

interface AlertProps {
  variant?: AlertVariant;
  message: string;
  className?: string;
}

const variantStyles: Record<AlertVariant, string> = {
  info: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-green-200 bg-green-50 text-green-800",
  error: "border-red-200 bg-red-50 text-red-800",
};

export function Alert({ variant = "info", message, className }: AlertProps) {
  return (
    <div className={cn("rounded-lg border px-3 py-2 text-sm", variantStyles[variant], className)} role="alert">
      {message}
    </div>
  );
}
