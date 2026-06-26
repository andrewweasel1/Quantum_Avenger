import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface EquityChartProps {
  equity: number[];
  height?: number;
}

/** Cumulative-return (equity) curve. Index on X, equity multiple on Y. */
export function EquityChart({ equity, height = 280 }: EquityChartProps) {
  if (!equity.length) {
    return (
      <div
        className="flex items-center justify-center text-sm text-muted-foreground"
        style={{ height }}
      >
        No equity data yet — run a backtest or wait for live trades.
      </div>
    );
  }
  const data = equity.map((value, index) => ({ index, value }));
  const positive = equity[equity.length - 1] >= (equity[0] ?? 1);
  const stroke = positive ? "hsl(var(--success))" : "hsl(var(--destructive))";

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={stroke} stopOpacity={0.35} />
            <stop offset="95%" stopColor={stroke} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="index"
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
          domain={["auto", "auto"]}
          tickFormatter={(v: number) => v.toFixed(2)}
        />
        <Tooltip
          formatter={(v: number) => [v.toFixed(4), "Equity"]}
          labelFormatter={(l) => `Bar ${l}`}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={stroke}
          strokeWidth={2}
          fill="url(#equityFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
