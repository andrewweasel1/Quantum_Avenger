import { KpiCard } from "@/components/KpiCard";
import { RegistryPanel } from "@/components/RegistryPanel";
import { RiskPanel } from "@/components/RiskPanel";
import { TradeLogTable } from "@/components/TradeLogTable";
import { VetoBarChart } from "@/components/VetoBarChart";
import { VetoLogTable } from "@/components/VetoLogTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useRegistry,
  useRisk,
  useTrades,
  useVetoes,
  useVetoLog,
} from "@/hooks/useApi";
import { formatNumber, formatPercent } from "@/lib/utils";

export function LiveMonitorPage() {
  const trades = useTrades();
  const vetoes = useVetoes();
  const vetoLog = useVetoLog();
  const risk = useRisk();
  const registry = useRegistry();
  const v = vetoes.data;

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Live Monitor</h1>
          <p className="text-sm text-muted-foreground">
            Executed trades, veto decisions, risk exposure, and the model registry.
          </p>
        </div>
        <span className="text-xs text-muted-foreground">Auto-refresh · 5s</span>
      </header>

      <Tabs defaultValue="trades">
        <TabsList>
          <TabsTrigger value="trades">Trades</TabsTrigger>
          <TabsTrigger value="vetoes">Vetoes</TabsTrigger>
          <TabsTrigger value="risk">Risk</TabsTrigger>
          <TabsTrigger value="registry">Registry</TabsTrigger>
        </TabsList>

        <TabsContent value="trades">
          <Card>
            <CardHeader>
              <CardTitle>Trade Log</CardTitle>
            </CardHeader>
            <CardContent>
              <TradeLogTable trades={trades.data ?? []} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vetoes">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <KpiCard label="Decisions" value={formatNumber(v?.total, 0)} />
              <KpiCard label="Executed" value={formatNumber(v?.executed, 0)} tone="positive" />
              <KpiCard label="Vetoed" value={formatNumber(v?.vetoed, 0)} tone="negative" />
              <KpiCard label="Veto Rate" value={formatPercent(v?.veto_rate, 1)} />
            </div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle>By Gate</CardTitle>
                </CardHeader>
                <CardContent>
                  <VetoBarChart byGate={v?.by_gate ?? {}} />
                </CardContent>
              </Card>
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Decision Ledger</CardTitle>
                </CardHeader>
                <CardContent>
                  <VetoLogTable vetoes={vetoLog.data ?? []} />
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="risk">
          <Card>
            <CardHeader>
              <CardTitle>Risk Exposure</CardTitle>
            </CardHeader>
            <CardContent>
              {risk.data && <RiskPanel risk={risk.data} />}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="registry">
          <Card>
            <CardHeader>
              <CardTitle>Model Registry</CardTitle>
            </CardHeader>
            <CardContent>
              {registry.data && <RegistryPanel registry={registry.data} />}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
