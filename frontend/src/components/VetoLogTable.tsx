import { Badge, type BadgeProps } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type VetoRow } from "@/lib/api";
import { formatNumber, formatTime } from "@/lib/utils";

const GATE_VARIANT: Record<string, BadgeProps["variant"]> = {
  none: "success",
  shield: "destructive",
  grader: "warning",
  execution: "default",
};

/** Per-decision veto ledger: which gate (if any) stopped each signal, and why. */
export function VetoLogTable({ vetoes }: { vetoes: VetoRow[] }) {
  if (!vetoes.length) {
    return <p className="text-sm text-muted-foreground">No decisions recorded yet.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Time</TableHead>
          <TableHead>Symbol</TableHead>
          <TableHead>Signal</TableHead>
          <TableHead>Gate</TableHead>
          <TableHead>Reason</TableHead>
          <TableHead className="text-right">DSR</TableHead>
          <TableHead className="text-right">Size</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {vetoes.map((v, i) => (
          <TableRow key={`${v.execution_id || v.symbol}-${i}`}>
            <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
              {formatTime(v.timestamp)}
            </TableCell>
            <TableCell className="font-medium">{v.symbol}</TableCell>
            <TableCell className="font-mono text-xs uppercase">{v.signal}</TableCell>
            <TableCell>
              <Badge variant={GATE_VARIANT[v.veto_gate] ?? "secondary"}>
                {v.veto_gate === "none" ? "executed" : v.veto_gate}
              </Badge>
            </TableCell>
            <TableCell className="max-w-[16rem] truncate text-xs text-muted-foreground">
              {v.veto_gate === "none" ? "—" : v.veto_reason}
            </TableCell>
            <TableCell className="text-right font-mono tabular-nums">{formatNumber(v.dsr)}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">{v.position_size}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
