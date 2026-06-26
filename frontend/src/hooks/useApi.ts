import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, type CreateRunRequest } from "@/lib/api";

const TERMINAL = ["done", "failed", "cancelled"];

export const useConfigSchema = () =>
  useQuery({ queryKey: ["config", "schema"], queryFn: api.configSchema, staleTime: Infinity });

export const useConfig = () =>
  useQuery({ queryKey: ["config", "current"], queryFn: api.config, staleTime: Infinity });

export const useRuns = () =>
  useQuery({ queryKey: ["runs"], queryFn: api.listRuns, refetchInterval: 4000 });

export function useRun(runId: string | null) {
  return useQuery({
    queryKey: ["runs", runId],
    queryFn: () => api.getRun(runId as string),
    enabled: !!runId,
    // Poll while the run is in flight; stop once it reaches a terminal state.
    refetchInterval: (query) =>
      query.state.data && TERMINAL.includes(query.state.data.status) ? false : 1500,
  });
}

export function useRunResults(runId: string | null, ready: boolean) {
  return useQuery({
    queryKey: ["runs", runId, "results"],
    queryFn: () => api.getResults(runId as string),
    enabled: !!runId && ready,
  });
}

export function useCreateRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateRunRequest) => api.createRun(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["runs"] }),
  });
}

const monitorOptions = { refetchInterval: 5000 };

export const useKpis = () =>
  useQuery({ queryKey: ["monitor", "kpis"], queryFn: api.kpis, ...monitorOptions });
export const usePerformance = () =>
  useQuery({ queryKey: ["monitor", "performance"], queryFn: api.performance, ...monitorOptions });
export const useVetoes = () =>
  useQuery({ queryKey: ["monitor", "vetoes"], queryFn: api.vetoes, ...monitorOptions });
export const useRisk = () =>
  useQuery({ queryKey: ["monitor", "risk"], queryFn: api.risk, ...monitorOptions });
export const useAlerts = () =>
  useQuery({ queryKey: ["monitor", "alerts"], queryFn: api.alerts, ...monitorOptions });
