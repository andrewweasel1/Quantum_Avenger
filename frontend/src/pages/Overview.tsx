import { Activity, Ban, Gauge, Percent, TrendingDown, Wallet } from "lucide-react";

import { AlertsList } from "@/components/AlertsList";
import { EquityChart } from "@/components/EquityChart";
import { KpiCard } from "@/components/KpiCard";
import { VetoBarChart } from "@/components/VetoBarChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAlerts, useKpis, usePerformance, useVetoes } from "@/hooks/useApi";
import { formatNumber, formatPercent } from "@/lib/utils";

export function Overview() {
  const kpis = useKpis();
  const performance = usePerformance();
  const vetoes = useVetoes();
  const alerts = useAlerts();

  const k = kpis.data;
  const drawdownTone = (k?.max_drawdown ?? 0) < -0.1 ? "negative" : "neutral";

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Overview</h1>
          <p className="text-sm text-muted-foreground">
            Live engine state from the veto ledger &amp; trade log.
          </p>
        </div>
        <span className="text-xs text-muted-foreground">Auto-refresh · 5s</span>
      </header>

      {alerts.data && <AlertsList alerts={alerts.data} />}

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard
          label="Total P&L"
          value={formatPercent(k?.total_pnl)}
          icon={Wallet}
          tone={(k?.total_pnl ?? 0) >= 0 ? "positive" : "negative"}
        />
        <KpiCard label="Sharpe" value={formatNumber(k?.sharpe)} icon={Gauge} />
        <KpiCard
          label="Max Drawdown"
          value={formatPercent(k?.max_drawdown)}
          icon={TrendingDown}
          tone={drawdownTone}
        />
        <KpiCard label="Veto Rate" value={formatPercent(k?.veto_rate, 1)} icon={Ban} />
        <KpiCard label="Win Rate" value={formatPercent(k?.win_rate, 1)} icon={Percent} />
        <KpiCard label="Profit Factor" value={formatNumber(k?.profit_factor)} icon={Activity} />
        <KpiCard label="Decisions" value={formatNumber(k?.total_decisions, 0)} />
        <KpiCard label="Executed" value={formatNumber(k?.executed, 0)} tone="positive" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Equity Curve</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityChart equity={performance.data?.equity_curve ?? []} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Vetoes by Gate</CardTitle>
          </CardHeader>
          <CardContent>
            <VetoBarChart byGate={vetoes.data?.by_gate ?? {}} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
