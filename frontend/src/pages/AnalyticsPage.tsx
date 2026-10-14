import { Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AlphaTable } from "@/components/AlphaTable";
import { DrawdownChart } from "@/components/DrawdownChart";
import { EquityChart } from "@/components/EquityChart";
import { KpiCard } from "@/components/KpiCard";
import { MetaLabelingPanel } from "@/components/MetaLabelingPanel";
import { PathFanChart } from "@/components/PathFanChart";
import { PortfolioDonut } from "@/components/PortfolioDonut";
import { PromotionTable } from "@/components/PromotionTable";
import { StatArbTable } from "@/components/StatArbTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRunResults, useRuns } from "@/hooks/useApi";
import { type SectorResult } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

export function AnalyticsPage() {
  const runs = useRuns();
  const doneRuns = useMemo(
    () => (runs.data ?? []).filter((r) => r.status === "done"),
    [runs.data],
  );
  const [runId, setRunId] = useState<string | null>(null);
  useEffect(() => {
    if (!runId && doneRuns.length) setRunId(doneRuns[0].run_id);
  }, [doneRuns, runId]);

  const results = useRunResults(runId, true);

  if (runs.isLoading) {
    return <Loading label="Loading runs…" />;
  }
  if (!doneRuns.length) {
    return (
      <Empty>
        No completed backtests yet. Launch one from the <strong>Engine Control</strong> panel,
        then come back to analyze it.
      </Empty>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Performance Analytics</h1>
          <p className="text-sm text-muted-foreground">
            Champion equity, drawdown, CPCV stability, signal edge, and promotion gates.
          </p>
        </div>
        <div className="w-72">
          <Select value={runId ?? ""} onValueChange={setRunId}>
            <SelectTrigger>
              <SelectValue placeholder="Select a run…" />
            </SelectTrigger>
            <SelectContent>
              {doneRuns.map((r) => (
                <SelectItem key={r.run_id} value={r.run_id}>
                  {r.run_id.slice(0, 8)} · {(r.created_at ?? "").slice(0, 16).replace("T", " ")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </header>

      {results.isLoading && <Loading label="Parsing artifacts…" />}
      {results.data && <ResultsView results={results.data} />}
    </div>
  );
}

function ResultsView({ results }: { results: import("@/lib/api").RunResults }) {
  const [slug, setSlug] = useState<string | null>(null);
  const sectors = results.sectors;
  const active = sectors.find((s) => s.slug === slug) ?? sectors[0];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Promotion Gates</CardTitle>
        </CardHeader>
        <CardContent>
          <PromotionTable promotions={results.promotions} />
        </CardContent>
      </Card>

      {active && (
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle>Champion Performance</CardTitle>
            {sectors.length > 1 && (
              <div className="w-60">
                <Select value={active.slug} onValueChange={setSlug}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {sectors.map((s) => (
                      <SelectItem key={s.slug} value={s.slug}>
                        {s.sector}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <SectorView sector={active} />
          </CardContent>
        </Card>
      )}

      {results.alpha_eval && Object.keys(results.alpha_eval.ic).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Signal Edge — IC / ICIR</CardTitle>
          </CardHeader>
          <CardContent>
            <AlphaTable alpha={results.alpha_eval} />
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {results.portfolio && (
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <PortfolioDonut portfolio={results.portfolio} />
            </CardContent>
          </Card>
        )}
        {results.stat_arb && (
          <Card>
            <CardHeader>
              <CardTitle>Statistical Arbitrage</CardTitle>
            </CardHeader>
            <CardContent>
              <StatArbTable statArb={results.stat_arb} />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function SectorView({ sector }: { sector: SectorResult }) {
  const m = sector.metrics;
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
        <KpiCard label="Sharpe" value={formatNumber(m.sharpe)} />
        <KpiCard label="Sortino" value={formatNumber(m.sortino)} />
        <KpiCard
          label="Max Drawdown"
          value={formatPercent(m.max_drawdown)}
          tone={m.max_drawdown < -0.1 ? "negative" : "neutral"}
        />
        <KpiCard label="Win Rate" value={formatPercent(m.win_rate, 1)} />
        <KpiCard label="Profit Factor" value={formatNumber(m.profit_factor)} />
        <KpiCard label="Trials" value={formatNumber(sector.n_trials, 0)} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Equity Curve">
          <EquityChart equity={sector.equity} height={220} />
        </Panel>
        <Panel title="Drawdown">
          <DrawdownChart equity={sector.equity} height={220} />
        </Panel>
      </div>

      <Panel title="CPCV Path Distribution">
        <PathFanChart paths={sector.paths ?? []} champion={sector.equity} />
      </Panel>

      {sector.meta_labeling && (
        <Panel title="Meta-Labeling — Precision / Recall">
          <MetaLabelingPanel meta={sector.meta_labeling} />
        </Panel>
      )}
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-background/40 p-4">
      <div className="mb-2 text-sm font-medium text-muted-foreground">{title}</div>
      {children}
    </div>
  );
}

function Loading({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" /> {label}
    </div>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Performance Analytics</h1>
      <Card>
        <CardContent className="py-10 text-center text-sm text-muted-foreground">
          {children}
        </CardContent>
      </Card>
    </div>
  );
}
