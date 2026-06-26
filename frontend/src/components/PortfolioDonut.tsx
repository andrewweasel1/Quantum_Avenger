import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { type Portfolio } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

const SLICE_COLORS = [
  "hsl(199 89% 48%)", "hsl(142 71% 45%)", "hsl(38 92% 50%)", "hsl(280 65% 60%)",
  "hsl(0 72% 51%)", "hsl(170 70% 45%)", "hsl(220 70% 60%)", "hsl(320 65% 55%)",
  "hsl(48 90% 55%)", "hsl(12 75% 55%)", "hsl(260 60% 62%)",
];

/** Cross-sector allocation weights of the combined book (HRP / NCO / etc.). */
export function PortfolioDonut({ portfolio }: { portfolio: Portfolio }) {
  const data = portfolio.sectors
    .map((sector) => ({ name: sector, value: Math.abs(portfolio.weights[sector] ?? 0) }))
    .filter((d) => d.value > 1e-9);
  if (!data.length) {
    return <p className="text-sm text-muted-foreground">No portfolio weights.</p>;
  }
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
        <span>method <span className="font-mono uppercase text-foreground">{portfolio.method}</span></span>
        <span>cov <span className="font-mono uppercase text-foreground">{portfolio.cov_method}</span></span>
        {portfolio.book_sharpe !== null && (
          <span>book Sharpe <span className="font-mono text-foreground">{formatNumber(portfolio.book_sharpe)}</span></span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
            stroke="hsl(var(--card))"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => formatPercent(v)} />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(value) => <span className="text-muted-foreground">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
