import { Line, LineChart } from "recharts";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type AlphaEval } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";

function DecaySparkline({ decay }: { decay: Record<string, number> | undefined }) {
  if (!decay || !Object.keys(decay).length) return <span className="text-muted-foreground">—</span>;
  const data = Object.entries(decay)
    .map(([h, ic]) => ({ h: Number(h), ic }))
    .sort((a, b) => a.h - b.h);
  return (
    <LineChart width={88} height={28} data={data} margin={{ top: 4, right: 2, left: 2, bottom: 4 }}>
      <Line
        type="monotone"
        dataKey="ic"
        stroke="hsl(var(--primary))"
        strokeWidth={1.5}
        dot={false}
        isAnimationActive={false}
      />
    </LineChart>
  );
}

/** Per-signal Information Coefficient / ICIR table — which signals actually carry edge. */
export function AlphaTable({ alpha }: { alpha: AlphaEval }) {
  const rows = Object.values(alpha.ic);
  if (!rows.length) {
    return <p className="text-sm text-muted-foreground">No signal diagnostics for this run.</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Signal</TableHead>
          <TableHead>Mean IC</TableHead>
          <TableHead>ICIR</TableHead>
          <TableHead>t-stat</TableHead>
          <TableHead>Breadth</TableHead>
          <TableHead>Hit rate</TableHead>
          <TableHead>Decay</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.signal}>
            <TableCell className="font-mono text-xs">{r.signal}</TableCell>
            <TableCell
              className={cn(
                "font-mono tabular-nums",
                r.mean_ic > 0 ? "text-success" : r.mean_ic < 0 ? "text-destructive" : "",
              )}
            >
              {formatNumber(r.mean_ic, 3)}
            </TableCell>
            <TableCell className="font-mono tabular-nums">{formatNumber(r.icir, 2)}</TableCell>
            <TableCell className="font-mono tabular-nums">{formatNumber(r.ic_t_stat, 2)}</TableCell>
            <TableCell className="font-mono tabular-nums">{formatNumber(r.breadth, 0)}</TableCell>
            <TableCell className="font-mono tabular-nums">{formatNumber(r.hit_rate, 2)}</TableCell>
            <TableCell>
              <DecaySparkline decay={alpha.decay[r.signal]} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
