import { Activity, LayoutDashboard, type LucideIcon, SlidersHorizontal } from "lucide-react";
import { type ReactNode } from "react";

import { cn } from "@/lib/utils";

export type PageKey = "overview" | "control";

interface NavItem {
  key: PageKey;
  label: string;
  icon: LucideIcon;
}

const NAV: NavItem[] = [
  { key: "overview", label: "Overview", icon: LayoutDashboard },
  { key: "control", label: "Engine Control", icon: SlidersHorizontal },
];

interface AppShellProps {
  page: PageKey;
  onNavigate: (page: PageKey) => void;
  children: ReactNode;
}

export function AppShell({ page, onNavigate, children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-card/40">
        <div className="flex items-center gap-2 px-5 py-5">
          <Activity className="h-6 w-6 text-primary" />
          <div>
            <div className="text-sm font-semibold leading-tight">Quantum Avenger</div>
            <div className="text-xs text-muted-foreground">Quant Engine Console</div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = page === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
        <div className="px-5 py-4 text-xs text-muted-foreground">
          Phase 1 · React + FastAPI
        </div>
      </aside>
      <main className="flex-1 overflow-x-hidden">
        <div className="mx-auto max-w-7xl px-8 py-8">{children}</div>
      </main>
    </div>
  );
}
