import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface PathFanChartProps {
  paths: number[][]; // each path is a per-bar equity curve from one CPCV recombination
  champion: number[]; // the headline champion equity, drawn bold over the fan
  height?: number;
}

/** The distribution of CPCV backtest paths (faint) under the champion curve (bold) —
 *  a visual read on how stable the edge is across recombinations of the folds. */
export function PathFanChart({ paths, champion, height = 240 }: PathFanChartProps) {
  if (!paths.length) {
    return (
      <div
        className="flex items-center justify-center text-sm text-muted-foreground"
        style={{ height }}
      >
        No CPCV paths recorded.
      </div>
    );
  }
  const length = Math.max(champion.length, ...paths.map((p) => p.length));
  const data = Array.from({ length }, (_, index) => {
    const row: Record<string, number> = { index };
    paths.forEach((path, p) => {
      if (index < path.length) row[`p${p}`] = path[index];
    });
    if (index < champion.length) row.champion = champion[index];
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
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
          tickFormatter={(v: number) => v.toFixed(2)}
        />
        <Tooltip formatter={(v: number) => v.toFixed(4)} labelFormatter={(l) => `Bar ${l}`} />
        {paths.map((_, p) => (
          <Line
            key={p}
            type="monotone"
            dataKey={`p${p}`}
            stroke="hsl(var(--primary))"
            strokeOpacity={0.18}
            strokeWidth={1}
            dot={false}
            isAnimationActive={false}
          />
        ))}
        <Line
          type="monotone"
          dataKey="champion"
          stroke="hsl(var(--primary))"
          strokeWidth={2.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
