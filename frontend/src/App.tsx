import { useState } from "react";

import { AppShell, type PageKey } from "@/components/AppShell";
import { ControlPanelPage } from "@/pages/ControlPanelPage";
import { Overview } from "@/pages/Overview";

export default function App() {
  const [page, setPage] = useState<PageKey>("overview");
  return (
    <AppShell page={page} onNavigate={setPage}>
      {page === "overview" ? <Overview /> : <ControlPanelPage />}
    </AppShell>
  );
}
