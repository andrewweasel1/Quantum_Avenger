import { CheckCircle2, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type PromotionEntry } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";

// Display thresholds mirroring the engine's promotion gates (config defaults).
function gateTone(value: number | null, pass: (v: number) => boolean): string {
  if (value === null) return "text-muted-foreground";
  return pass(value) ? "text-success" : "text-destructive";
}

function Gate({ value, pass, digits = 2 }: {
  value: number | null;
  pass: (v: number) => boolean;
  digits?: number;
}) {
  return (
    <span className={cn("font-mono tabular-nums", gateTone(value, pass))}>
      {formatNumber(value, digits)}
    </span>
  );
}

export function PromotionTable({ promotions }: { promotions: PromotionEntry[] }) {
  if (!promotions.length) {
    return <p className="text-sm text-muted-foreground">No promotion decisions recorded.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Sector</TableHead>
          <TableHead>Verdict</TableHead>
          <TableHead>DSR</TableHead>
          <TableHead>PBO</TableHead>
          <TableHead>PSR</TableHead>
          <TableHead>Haircut SR</TableHead>
          <TableHead>Path pass</TableHead>
          <TableHead>Reason</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {promotions.map((p) => (
          <TableRow key={`${p.sector}-${p.timestamp ?? ""}`}>
            <TableCell className="font-medium">{p.sector}</TableCell>
            <TableCell>
              {p.promoted ? (
                <Badge variant="success" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" /> promoted
                </Badge>
              ) : (
                <Badge variant="destructive" className="gap-1">
                  <XCircle className="h-3 w-3" /> rejected
                </Badge>
              )}
            </TableCell>
            <TableCell><Gate value={p.dsr} pass={(v) => v >= 0.95} /></TableCell>
            <TableCell><Gate value={p.pbo} pass={(v) => v <= 0.5} /></TableCell>
            <TableCell><Gate value={p.psr} pass={(v) => v >= 0.95} /></TableCell>
            <TableCell><Gate value={p.haircut_sharpe} pass={(v) => v > 0} /></TableCell>
            <TableCell><Gate value={p.cpcv_path_pass_fraction} pass={(v) => v >= 0.5} /></TableCell>
            <TableCell className="max-w-[14rem] truncate text-xs text-muted-foreground">
              {p.promoted ? "all gates passed" : p.reason}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
