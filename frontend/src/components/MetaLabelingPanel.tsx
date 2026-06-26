import { Badge } from "@/components/ui/badge";
import { type MetaLabeling } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";

function Cell({ value, better }: { value: number; better?: boolean }) {
  return (
    <td className={cn("px-3 py-1.5 text-right font-mono tabular-nums", better && "text-success")}>
      {formatNumber(value, 3)}
    </td>
  );
}

/** Meta-labeling diagnostic: does a secondary "act / don't act" model improve the
 *  primary triple-barrier signal's precision/recall (out-of-sample)? */
export function MetaLabelingPanel({ meta }: { meta: MetaLabeling }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          Fired {meta.n_fired_test} bars OOS ({meta.n_fired_train} train)
        </span>
        <Badge variant={meta.improved ? "success" : "secondary"}>
          {meta.improved ? "meta improves" : "no improvement"}
        </Badge>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-xs text-muted-foreground">
            <th className="px-3 py-1.5 text-left font-medium">Model</th>
            <th className="px-3 py-1.5 text-right font-medium">Precision</th>
            <th className="px-3 py-1.5 text-right font-medium">Recall</th>
            <th className="px-3 py-1.5 text-right font-medium">F1</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-t border-border">
            <td className="px-3 py-1.5">Primary</td>
            <Cell value={meta.precision_primary} />
            <Cell value={meta.recall_primary} />
            <Cell value={meta.f1_primary} />
          </tr>
          <tr className="border-t border-border">
            <td className="px-3 py-1.5">Meta-filtered</td>
            <Cell value={meta.precision_meta} better={meta.precision_meta > meta.precision_primary} />
            <Cell value={meta.recall_meta} better={meta.recall_meta > meta.recall_primary} />
            <Cell value={meta.f1_meta} better={meta.f1_meta > meta.f1_primary} />
          </tr>
        </tbody>
      </table>
    </div>
  );
}
