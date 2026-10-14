import { Layers, Maximize2, PieChart, Wallet } from "lucide-react";

import { KpiCard } from "@/components/KpiCard";
import { type RiskView } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

/** Live portfolio risk: gross notional, open positions, and concentration. */
export function RiskPanel({ risk }: { risk: RiskView }) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <KpiCard
        label="Gross Exposure"
        value={`$${formatNumber(risk.gross_exposure, 0)}`}
        icon={Wallet}
      />
      <KpiCard label="Open Positions" value={formatNumber(risk.position_count, 0)} icon={Layers} />
      <KpiCard
        label="Largest Position"
        value={`$${formatNumber(risk.largest_position, 0)}`}
        icon={Maximize2}
      />
      <KpiCard
        label="Concentration"
        value={formatPercent(risk.concentration, 1)}
        icon={PieChart}
        tone={risk.concentration > 0.5 ? "negative" : "neutral"}
        hint="largest / gross"
      />
    </div>
  );
}
