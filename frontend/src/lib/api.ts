// Typed client for the Quantum Avenger FastAPI backend. Paths are same-origin:
// the Vite dev server proxies /api -> uvicorn; in production FastAPI serves both.

export type ControlType =
  | "slider"
  | "switch"
  | "select"
  | "multiselect"
  | "number"
  | "text";

export interface SchemaField {
  name: string;
  type: "bool" | "int" | "float" | "str" | "list";
  default: unknown;
  control: ControlType;
  description: string;
  options: string[] | null;
  min: number | null;
  max: number | null;
  step: number | null;
  tunable: boolean;
}

export interface SchemaGroup {
  key: string;
  label: string;
  primary: boolean;
  fields: SchemaField[];
}

export interface ConfigSchema {
  groups: SchemaGroup[];
}

export type ConfigValues = Record<string, Record<string, unknown>>;

export interface RunParams {
  start: string;
  end: string;
  max_symbols: number | null;
}

export interface RunStatus {
  run_id: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  started_at?: string;
  finished_at?: string;
  created_at?: string;
  n_sectors?: number;
  n_promoted?: number;
  error?: string;
  params?: Partial<RunParams>;
}

export interface SectorMetrics {
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
}

export interface MetaLabeling {
  precision_primary: number;
  recall_primary: number;
  f1_primary: number;
  precision_meta: number;
  recall_meta: number;
  f1_meta: number;
  improved: boolean;
  n_fired_train: number;
  n_fired_test: number;
}

export interface SectorResult {
  sector: string;
  slug: string;
  equity: number[];
  metrics: SectorMetrics;
  n_trials: number;
  paths?: number[][];
  meta_labeling?: MetaLabeling | null;
}

// A promotion-registry audit entry: the champion's gate scores + the verdict.
export interface PromotionEntry {
  sector: string;
  dsr: number | null;
  synthetic_sharpe: number | null;
  pbo: number | null;
  psr: number | null;
  haircut_sharpe: number | null;
  cpcv_path_pass_fraction: number | null;
  cpcv_path_dsr_median: number | null;
  reality_check_pvalue: number | null;
  promoted: boolean;
  reason: string;
  timestamp?: string;
  model_path?: string | null;
}

export interface ICReport {
  signal: string;
  mean_ic: number;
  icir: number;
  ic_t_stat: number;
  n_periods: number;
  breadth: number;
  hit_rate: number;
}

export interface AlphaEval {
  ic: Record<string, ICReport>;
  decay: Record<string, Record<string, number>>;
  min_names: number;
  n_signals: number;
}

export interface Portfolio {
  sectors: string[];
  weights: Record<string, number>;
  method: string;
  cov_method: string;
  book_sharpe: number | null;
  sector_sharpe: Record<string, number>;
  n_obs: number;
}

export interface StatArbPair {
  name: string;
  y: string;
  x: string;
  sector: string;
  hedge_ratio: number | null;
  adf_tstat: number | null;
  half_life: number | null;
  validated: boolean;
}

export interface StatArb {
  pairs: StatArbPair[];
  n_pairs: number;
  n_candidates: number;
  n_validated: number;
  reality_check_pvalue: number | null;
  book_sharpe: number | null;
}

export interface RunResults {
  run_id: string;
  summary: Record<string, unknown>;
  promotions: PromotionEntry[];
  active_champions: Record<string, string>;
  alpha_eval: AlphaEval | null;
  portfolio: Portfolio | null;
  stat_arb: StatArb | null;
  sectors: SectorResult[];
}

export interface Kpis {
  total_decisions: number;
  executed: number;
  vetoed: number;
  veto_rate: number;
  total_pnl: number;
  sharpe: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
}

export interface Performance {
  total_pnl: number;
  sharpe: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  equity_curve: number[];
}

export interface VetoSummary {
  total: number;
  executed: number;
  vetoed: number;
  veto_rate: number;
  by_gate: Record<string, number>;
}

export interface RiskView {
  gross_exposure: number;
  position_count: number;
  largest_position: number;
  concentration: number;
}

export interface Alert {
  severity: "warning" | "critical";
  message: string;
}

export interface TradeRow {
  symbol: string;
  side: string;
  qty: number;
  limit_price: number;
  status: string;
  order_id: string;
  fill_price: number;
  pnl: number;
  timestamp?: string | null;
}

export interface VetoRow {
  symbol: string;
  signal: string;
  entry_price: number;
  veto_reason: string;
  veto_gate: string;
  dsr: number | null;
  position_size: number;
  execution_id: string;
  timestamp?: string | null;
}

export interface Registry {
  active_champions: Record<string, string>;
  promotions: PromotionEntry[];
}

export interface CreateRunRequest {
  params: RunParams;
  overrides: ConfigValues;
  seed?: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    let detail: unknown;
    try {
      detail = (await response.json())?.detail;
    } catch {
      detail = response.statusText;
    }
    throw new Error(typeof detail === "string" ? detail : `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  configSchema: () => request<ConfigSchema>("/api/config/schema"),
  config: () => request<ConfigValues>("/api/config"),

  createRun: (body: CreateRunRequest) =>
    request<RunStatus>("/api/runs", { method: "POST", body: JSON.stringify(body) }),
  listRuns: () => request<RunStatus[]>("/api/runs"),
  getRun: (id: string) => request<RunStatus>(`/api/runs/${id}`),
  getResults: (id: string) => request<RunResults>(`/api/runs/${id}/results`),
  cancelRun: (id: string) =>
    request<{ run_id: string; cancelled: boolean }>(`/api/runs/${id}`, { method: "DELETE" }),

  kpis: () => request<Kpis>("/api/monitor/kpis"),
  performance: () => request<Performance>("/api/monitor/performance"),
  vetoes: () => request<VetoSummary>("/api/monitor/vetoes"),
  risk: () => request<RiskView>("/api/monitor/risk"),
  alerts: () => request<Alert[]>("/api/monitor/alerts"),
  trades: () => request<TradeRow[]>("/api/monitor/trades"),
  vetoLog: () => request<VetoRow[]>("/api/monitor/veto-log"),
  registry: () => request<Registry>("/api/monitor/registry"),
};
