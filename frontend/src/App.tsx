import { useState } from "react";

import { AppShell, type PageKey } from "@/components/AppShell";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { ControlPanelPage } from "@/pages/ControlPanelPage";
import { Overview } from "@/pages/Overview";

export default function App() {
  const [page, setPage] = useState<PageKey>("overview");
  return (
    <AppShell page={page} onNavigate={setPage}>
      {page === "overview" && <Overview />}
      {page === "analytics" && <AnalyticsPage />}
      {page === "control" && <ControlPanelPage />}
    </AppShell>
  );
}
