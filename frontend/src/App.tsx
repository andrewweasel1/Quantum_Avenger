import { useState } from "react";

import { AppShell, type PageKey } from "@/components/AppShell";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { ControlPanelPage } from "@/pages/ControlPanelPage";
import { LiveMonitorPage } from "@/pages/LiveMonitorPage";
import { Overview } from "@/pages/Overview";

export default function App() {
  const [page, setPage] = useState<PageKey>("overview");
  return (
    <AppShell page={page} onNavigate={setPage}>
      {page === "overview" && <Overview />}
      {page === "analytics" && <AnalyticsPage />}
      {page === "monitor" && <LiveMonitorPage />}
      {page === "control" && <ControlPanelPage />}
    </AppShell>
  );
}
