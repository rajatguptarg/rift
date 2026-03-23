import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

export function useExecutionStream(batchChangeId: string, runId: string): void {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!batchChangeId || !runId) return;

    const url = `/api/v1/batch-changes/${batchChangeId}/runs/${runId}/stream`;
    const es = new EventSource(url);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string);
        if (data.event === "done") {
          es.close();
          return;
        }
        // Update workspace executions cache in place
        queryClient.setQueryData<unknown[]>(
          ["workspace-executions", runId],
          (old) => {
            if (!Array.isArray(old)) return old;
            return old.map((we: Record<string, unknown>) =>
              we.id === data.id ? { ...we, ...data } : we
            );
          }
        );
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      es.close();
    };

    return () => {
      es.close();
    };
  }, [batchChangeId, runId, queryClient]);
}
