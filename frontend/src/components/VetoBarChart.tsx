import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const GATE_COLORS: Record<string, string> = {
  shield: "hsl(var(--destructive))",
  grader: "hsl(var(--warning))",
  execution: "hsl(var(--primary))",
};

interface VetoBarChartProps {
  byGate: Record<string, number>;
  height?: number;
}

/** Counts of vetoes broken down by the gate that rejected the trade. */
export function VetoBarChart({ byGate, height = 240 }: VetoBarChartProps) {
  const data = Object.entries(byGate).map(([gate, count]) => ({ gate, count }));
  if (!data.length) {
    return (
      <div
        className="flex items-center justify-center text-sm text-muted-foreground"
        style={{ height }}
      >
        No vetoes recorded.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="gate"
          tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          allowDecimals={false}
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip cursor={{ fill: "hsl(var(--accent))", opacity: 0.4 }} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.gate} fill={GATE_COLORS[entry.gate] ?? "hsl(var(--muted-foreground))"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
