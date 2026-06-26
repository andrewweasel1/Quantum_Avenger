import { AlertTriangle, ShieldCheck } from "lucide-react";

import { type Alert } from "@/lib/api";
import { cn } from "@/lib/utils";

export function AlertsList({ alerts }: { alerts: Alert[] }) {
  if (!alerts.length) {
    return (
      <div className="flex items-center gap-2 rounded-md border border-border bg-success/10 px-4 py-3 text-sm text-success">
        <ShieldCheck className="h-4 w-4" />
        All clear — no thresholds breached.
      </div>
    );
  }
  return (
    <div className="space-y-2">
      {alerts.map((alert, index) => (
        <div
          key={index}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-3 text-sm",
            alert.severity === "critical"
              ? "border-destructive/40 bg-destructive/10 text-destructive"
              : "border-warning/40 bg-warning/10 text-warning",
          )}
        >
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{alert.message}</span>
        </div>
      ))}
    </div>
  );
}
