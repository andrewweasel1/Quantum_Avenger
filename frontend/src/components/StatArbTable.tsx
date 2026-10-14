import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type StatArb } from "@/lib/api";
import { formatNumber } from "@/lib/utils";

/** Cointegrated stat-arb pairs found this run, with their fit diagnostics. */
export function StatArbTable({ statArb }: { statArb: StatArb }) {
  if (!statArb.pairs?.length) {
    return <p className="text-sm text-muted-foreground">No cointegrated pairs found.</p>;
  }
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
        <span>{statArb.n_pairs} pairs / {statArb.n_candidates} searched</span>
        <span>{statArb.n_validated} validated</span>
        {statArb.book_sharpe !== null && (
          <span>book Sharpe <span className="font-mono text-foreground">{formatNumber(statArb.book_sharpe)}</span></span>
        )}
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Pair</TableHead>
            <TableHead>Sector</TableHead>
            <TableHead>Hedge ratio</TableHead>
            <TableHead>ADF t-stat</TableHead>
            <TableHead>Half-life</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {statArb.pairs.map((pair) => (
            <TableRow key={pair.name}>
              <TableCell className="font-mono text-xs">{pair.y} ~ {pair.x}</TableCell>
              <TableCell className="text-xs">{pair.sector}</TableCell>
              <TableCell className="font-mono tabular-nums">{formatNumber(pair.hedge_ratio)}</TableCell>
              <TableCell className="font-mono tabular-nums">{formatNumber(pair.adf_tstat)}</TableCell>
              <TableCell className="font-mono tabular-nums">{formatNumber(pair.half_life, 1)}</TableCell>
              <TableCell>
                <Badge variant={pair.validated ? "success" : "secondary"}>
                  {pair.validated ? "validated" : "candidate"}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
