import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { IDECodePanel } from "../../components/ui/IDECodePanel.tsx";
import { TelemetryChip } from "../../components/ui/TelemetryChip.tsx";
import { useExecutionStream } from "../../hooks/useExecutionStream.ts";
import { api } from "../../services/api.ts";

interface WorkspaceExecution {
  id: string;
  repo_ref: string;
  state: string;
  duration_seconds: number | null;
  error_message: string | null;
}

export default function ExecutionView() {
  const { id: batchChangeId, runId } = useParams<{ id: string; runId: string }>();

  const { data: executions } = useQuery({
    queryKey: ["workspace-executions", runId],
    queryFn: () =>
      api
        .get<WorkspaceExecution[]>(
          `/api/v1/batch-changes/${batchChangeId}/runs/${runId}/workspaces`
        )
        .then((r) => r.data),
    refetchInterval: 5000,
  });

  // SSE stream hook updates the cache in real-time
  useExecutionStream(batchChangeId!, runId!);

  const [expandedId, setExpandedId] = React.useState<string | null>(null);

  return (
    <div className="px-12 py-12">
      <div className="mb-8 flex items-center gap-4">
        <h1 className="font-headline text-3xl font-extrabold uppercase tracking-widest text-on-surface">
          Execution Run
        </h1>
        <span className="font-mono text-xs text-on-surface-variant">{runId}</span>
      </div>

      <div className="space-y-px">
        {(executions ?? []).map((we) => (
          <div key={we.id} className="bg-surface-container-low">
            {/* Row */}
            <button
              className="flex w-full items-center gap-4 px-6 py-3 hover:bg-surface-container transition-colors"
              onClick={() => setExpandedId(expandedId === we.id ? null : we.id)}
            >
              <TelemetryChip status={we.state} />
              <span className="flex-1 text-left font-mono text-sm text-on-surface">
                {we.repo_ref}
              </span>
              {we.duration_seconds != null && (
                <span className="font-mono text-xs text-on-surface-variant">
                  {we.duration_seconds.toFixed(1)}s
                </span>
              )}
              <span className="material-symbols-outlined text-sm text-on-surface-variant">
                {expandedId === we.id ? "expand_less" : "expand_more"}
              </span>
            </button>

            {/* Expanded log */}
            {expandedId === we.id && (
              <IDECodePanel className="max-h-64 overflow-auto border-t border-surface-container-highest">
                {we.error_message ? (
                  <span className="text-error font-mono text-xs">{we.error_message}</span>
                ) : (
                  <span className="text-on-surface-variant font-mono text-xs">
                    No log data yet. Streaming logs will appear here during execution.
                  </span>
                )}
              </IDECodePanel>
            )}
          </div>
        ))}

        {(executions ?? []).length === 0 && (
          <p className="py-12 text-center font-mono text-sm text-on-surface-variant">
            Waiting for workspace executions to begin...
          </p>
        )}
      </div>
    </div>
  );
}
