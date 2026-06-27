import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type TradeRow } from "@/lib/api";
import { cn, formatNumber, formatPercent, formatTime } from "@/lib/utils";

/** The executed trade log: fills, status, and realized P&L per order. */
export function TradeLogTable({ trades }: { trades: TradeRow[] }) {
  if (!trades.length) {
    return <p className="text-sm text-muted-foreground">No trades recorded yet.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Time</TableHead>
          <TableHead>Symbol</TableHead>
          <TableHead>Side</TableHead>
          <TableHead className="text-right">Qty</TableHead>
          <TableHead className="text-right">Limit</TableHead>
          <TableHead className="text-right">Fill</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">P&amp;L</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {trades.map((t, i) => (
          <TableRow key={`${t.order_id}-${i}`}>
            <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
              {formatTime(t.timestamp)}
            </TableCell>
            <TableCell className="font-medium">{t.symbol}</TableCell>
            <TableCell>
              <span className={cn("font-mono text-xs uppercase",
                t.side === "buy" ? "text-success" : "text-destructive")}>
                {t.side}
              </span>
            </TableCell>
            <TableCell className="text-right font-mono tabular-nums">{t.qty}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">{formatNumber(t.limit_price)}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">{formatNumber(t.fill_price)}</TableCell>
            <TableCell>
              <Badge variant={t.status === "filled" ? "success" : "secondary"}>{t.status}</Badge>
            </TableCell>
            <TableCell
              className={cn("text-right font-mono tabular-nums",
                t.pnl > 0 ? "text-success" : t.pnl < 0 ? "text-destructive" : "")}
            >
              {formatPercent(t.pnl)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
