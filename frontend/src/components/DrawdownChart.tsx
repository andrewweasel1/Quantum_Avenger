import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { drawdownSeries, formatPercent } from "@/lib/utils";

/** Underwater (drawdown) curve derived from an equity series. */
export function DrawdownChart({ equity, height = 200 }: { equity: number[]; height?: number }) {
  if (!equity.length) {
    return (
      <div
        className="flex items-center justify-center text-sm text-muted-foreground"
        style={{ height }}
      >
        No data.
      </div>
    );
  }
  const data = drawdownSeries(equity).map((value, index) => ({ index, value }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
        <defs>
          <linearGradient id="ddFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.05} />
            <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0.4} />
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
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
        />
        <Tooltip
          formatter={(v: number) => [formatPercent(v), "Drawdown"]}
          labelFormatter={(l) => `Bar ${l}`}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="hsl(var(--destructive))"
          strokeWidth={1.5}
          fill="url(#ddFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
