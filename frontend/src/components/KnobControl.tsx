import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { type SchemaField } from "@/lib/api";
import { cn } from "@/lib/utils";

interface KnobControlProps {
  field: SchemaField;
  value: unknown;
  onChange: (value: unknown) => void;
}

/** Render one config field as the control its schema metadata prescribes. */
export function KnobControl({ field, value, onChange }: KnobControlProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-3">
        <Label htmlFor={field.name} className="text-sm">
          <span className="font-mono text-xs text-muted-foreground">{field.name}</span>
        </Label>
        <Control field={field} value={value} onChange={onChange} />
      </div>
      {field.description && <p className="text-xs text-muted-foreground">{field.description}</p>}
    </div>
  );
}

function Control({ field, value, onChange }: KnobControlProps) {
  switch (field.control) {
    case "switch":
      return (
        <Switch
          id={field.name}
          checked={Boolean(value)}
          onCheckedChange={(checked) => onChange(checked)}
        />
      );

    case "slider": {
      const min = field.min ?? 0;
      const max = field.max ?? 100;
      const step = field.step ?? (field.type === "int" ? 1 : 0.01);
      const current = typeof value === "number" ? value : Number(field.default ?? min);
      return (
        <div className="flex w-48 items-center gap-3">
          <Slider
            id={field.name}
            min={min}
            max={max}
            step={step}
            value={[current]}
            onValueChange={([next]) => onChange(field.type === "int" ? Math.round(next) : next)}
          />
          <span className="w-12 shrink-0 text-right font-mono text-xs tabular-nums">
            {typeof current === "number" ? current : "—"}
          </span>
        </div>
      );
    }

    case "select":
      return (
        <Select value={String(value ?? "")} onValueChange={(next) => onChange(next)}>
          <SelectTrigger id={field.name} className="w-48">
            <SelectValue placeholder="Select…" />
          </SelectTrigger>
          <SelectContent>
            {(field.options ?? []).map((option) => (
              <SelectItem key={option} value={option}>
                {option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      );

    case "multiselect": {
      const selected = Array.isArray(value) ? (value as string[]) : [];
      const toggle = (option: string) =>
        onChange(
          selected.includes(option)
            ? selected.filter((o) => o !== option)
            : [...selected, option],
        );
      return (
        <div className="flex max-w-md flex-wrap justify-end gap-1.5">
          {(field.options ?? []).map((option) => {
            const active = selected.includes(option);
            return (
              <button
                key={option}
                type="button"
                onClick={() => toggle(option)}
                className={cn(
                  "rounded-full border px-2.5 py-0.5 font-mono text-xs transition-colors",
                  active
                    ? "border-primary bg-primary/15 text-primary"
                    : "border-border text-muted-foreground hover:border-primary/50",
                )}
              >
                {option}
              </button>
            );
          })}
        </div>
      );
    }

    case "number":
      return (
        <Input
          id={field.name}
          type="number"
          className="w-48"
          step={field.step ?? (field.type === "int" ? 1 : "any")}
          value={value === null || value === undefined ? "" : String(value)}
          onChange={(e) => {
            const raw = e.target.value;
            onChange(raw === "" ? null : field.type === "int" ? parseInt(raw, 10) : parseFloat(raw));
          }}
        />
      );

    default:
      return (
        <Input
          id={field.name}
          className="w-48"
          value={value === null || value === undefined ? "" : String(value)}
          onChange={(e) => onChange(e.target.value)}
        />
      );
  }
}
