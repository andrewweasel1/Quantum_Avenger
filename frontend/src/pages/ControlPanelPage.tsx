import { Loader2, Play, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

import { EquityChart } from "@/components/EquityChart";
import { KnobControl } from "@/components/KnobControl";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConfig, useConfigSchema, useCreateRun, useRun, useRunResults } from "@/hooks/useApi";
import { type ConfigValues, type RunStatus, type SchemaGroup } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

type Overrides = Record<string, Record<string, unknown>>;

const STATUS_VARIANT: Record<RunStatus["status"], "default" | "success" | "warning" | "destructive"> =
  {
    queued: "warning",
    running: "warning",
    done: "success",
    failed: "destructive",
    cancelled: "destructive",
  };

export function ControlPanelPage() {
  const schema = useConfigSchema();
  const config = useConfig();
  const createRun = useCreateRun();
  const [overrides, setOverrides] = useState<Overrides>({});
  const [params, setParams] = useState({ start: "2021-01-01", end: "2021-06-30", max_symbols: 4 });
  const [runId, setRunId] = useState<string | null>(null);

  const run = useRun(runId);
  const status = run.data?.status;
  const results = useRunResults(runId, status === "done");

  const primaryGroups = useMemo(
    () => (schema.data?.groups ?? []).filter((g) => g.primary && g.fields.some((f) => f.tunable)),
    [schema.data],
  );

  const effectiveValue = (group: string, name: string, fallback: unknown) => {
    if (overrides[group] && name in overrides[group]) return overrides[group][name];
    const live = (config.data as ConfigValues | undefined)?.[group]?.[name];
    return live !== undefined ? live : fallback;
  };

  const setValue = (group: string, name: string, value: unknown) =>
    setOverrides((prev) => ({ ...prev, [group]: { ...prev[group], [name]: value } }));

  const launch = async () => {
    const created = await createRun.mutateAsync({
      params: { start: params.start, end: params.end, max_symbols: params.max_symbols },
      overrides,
    });
    setRunId(created.run_id);
  };

  const changedCount = Object.values(overrides).reduce((n, g) => n + Object.keys(g).length, 0);
  const busy = status === "queued" || status === "running" || createRun.isPending;

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Engine Control Panel</h1>
          <p className="text-sm text-muted-foreground">
            Tune the engine's knobs and launch an isolated backtest.
          </p>
        </div>
        {changedCount > 0 && (
          <Button variant="ghost" size="sm" onClick={() => setOverrides({})}>
            <RotateCcw className="h-4 w-4" /> Reset {changedCount} override{changedCount > 1 ? "s" : ""}
          </Button>
        )}
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {schema.isLoading ? (
            <Card>
              <CardContent className="flex items-center gap-2 py-10 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading schema…
              </CardContent>
            </Card>
          ) : (
            <KnobGroups
              groups={primaryGroups}
              effectiveValue={effectiveValue}
              setValue={setValue}
            />
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Run a Backtest</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="start">Start</Label>
                  <Input
                    id="start"
                    type="date"
                    value={params.start}
                    onChange={(e) => setParams({ ...params, start: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="end">End</Label>
                  <Input
                    id="end"
                    type="date"
                    value={params.end}
                    onChange={(e) => setParams({ ...params, end: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="max_symbols">Max sectors</Label>
                <Input
                  id="max_symbols"
                  type="number"
                  min={1}
                  value={params.max_symbols}
                  onChange={(e) =>
                    setParams({ ...params, max_symbols: parseInt(e.target.value || "1", 10) })
                  }
                />
              </div>
              <Button className="w-full" onClick={launch} disabled={busy}>
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                {busy ? "Running…" : "Run Backtest"}
              </Button>
              {createRun.isError && (
                <p className="text-xs text-destructive">{(createRun.error as Error).message}</p>
              )}
              {changedCount > 0 && (
                <p className="text-xs text-muted-foreground">
                  {changedCount} config override{changedCount > 1 ? "s" : ""} will be applied.
                </p>
              )}
            </CardContent>
          </Card>

          {runId && <RunStatusCard run={run.data} results={results.data} />}
        </div>
      </div>
    </div>
  );
}

interface KnobGroupsProps {
  groups: SchemaGroup[];
  effectiveValue: (group: string, name: string, fallback: unknown) => unknown;
  setValue: (group: string, name: string, value: unknown) => void;
}

function KnobGroups({ groups, effectiveValue, setValue }: KnobGroupsProps) {
  if (!groups.length) return null;
  return (
    <Tabs defaultValue={groups[0].key}>
      <TabsList className="flex w-full flex-wrap">
        {groups.map((group) => (
          <TabsTrigger key={group.key} value={group.key}>
            {group.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {groups.map((group) => (
        <TabsContent key={group.key} value={group.key}>
          <Card>
            <CardContent className="space-y-4 py-5">
              {group.fields
                .filter((f) => f.tunable)
                .map((field) => (
                  <KnobControl
                    key={field.name}
                    field={field}
                    value={effectiveValue(group.key, field.name, field.default)}
                    onChange={(value) => setValue(group.key, field.name, value)}
                  />
                ))}
            </CardContent>
          </Card>
        </TabsContent>
      ))}
    </Tabs>
  );
}

function RunStatusCard({
  run,
  results,
}: {
  run: RunStatus | undefined;
  results: ReturnType<typeof useRunResults>["data"];
}) {
  if (!run) return null;
  const champion = results?.sectors?.[0];
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Run {run.run_id.slice(0, 8)}</CardTitle>
        <Badge variant={STATUS_VARIANT[run.status]}>{run.status}</Badge>
      </CardHeader>
      <CardContent className="space-y-3">
        {run.status === "failed" && (
          <p className="font-mono text-xs text-destructive">{run.error}</p>
        )}
        {run.status === "done" && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <Metric label="Sectors" value={formatNumber(run.n_sectors, 0)} />
            <Metric label="Promoted" value={formatNumber(run.n_promoted, 0)} />
          </div>
        )}
        {champion && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground">
              Champion · {champion.sector}
            </div>
            <EquityChart equity={champion.equity} height={140} />
            <div className="grid grid-cols-3 gap-2 text-center">
              <Metric label="Sharpe" value={formatNumber(champion.metrics.sharpe)} />
              <Metric label="Sortino" value={formatNumber(champion.metrics.sortino)} />
              <Metric label="Max DD" value={formatPercent(champion.metrics.max_drawdown)} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-muted/40 px-2 py-1.5">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-mono text-sm font-semibold tabular-nums">{value}</div>
    </div>
  );
}
