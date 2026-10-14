import { PromotionTable } from "@/components/PromotionTable";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type Registry } from "@/lib/api";

/** The immutable promotion registry: current champions + the full audit history. */
export function RegistryPanel({ registry }: { registry: Registry }) {
  const champions = Object.entries(registry.active_champions);
  return (
    <div className="space-y-6">
      <div>
        <div className="mb-2 text-sm font-medium text-muted-foreground">
          Active Champions ({champions.length})
        </div>
        {champions.length ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sector</TableHead>
                <TableHead>Model</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {champions.map(([sector, path]) => (
                <TableRow key={sector}>
                  <TableCell className="font-medium">{sector}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {path?.split("/").pop() ?? path}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <p className="text-sm text-muted-foreground">No champions promoted yet.</p>
        )}
      </div>

      <div>
        <div className="mb-2 text-sm font-medium text-muted-foreground">
          Promotion History ({registry.promotions.length})
        </div>
        <PromotionTable promotions={registry.promotions} />
      </div>
    </div>
  );
}
