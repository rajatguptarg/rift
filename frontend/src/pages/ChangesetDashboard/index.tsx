import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { TelemetryChip } from "../../components/ui/TelemetryChip.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { BurndownChart } from "../../components/BurndownChart.tsx";
import { ChangesetBulkActions } from "../../components/ChangesetBulkActions.tsx";
import { ImportChangesets } from "./ImportChangesets.tsx";
import { api } from "../../services/api.ts";

interface Changeset {
  id: string;
  repo_ref: string;
  state: string;
  title: string;
  external_url: string | null;
  review_state: string;
  ci_state: string;
}

interface Stats {
  total: number;
  merged: number;
  open: number;
}

export default function ChangesetDashboard() {
  const { id: batchChangeId } = useParams<{ id: string }>();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [importOpen, setImportOpen] = useState(false);

  const { data: changesets } = useQuery({
    queryKey: ["changesets", batchChangeId],
    queryFn: () =>
      api
        .get<{ items: Changeset[] }>(`/api/v1/batch-changes/${batchChangeId}/changesets`)
        .then((r) => r.data),
    refetchInterval: 30_000,
  });

  const { data: stats } = useQuery({
    queryKey: ["stats", batchChangeId],
    queryFn: () =>
      api.get<Stats>(`/api/v1/batch-changes/${batchChangeId}/stats`).then((r) => r.data),
  });

  const items = changesets?.items ?? [];
  const pctMerged = stats ? Math.round((stats.merged / Math.max(1, stats.total)) * 100) : 0;

  const toggleSelect = (id: string) => {
    setSelected((s) => {
      const next = new Set(s);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="px-12 py-12">
      <div className="mb-8 flex items-start justify-between">
        <h1 className="font-headline text-4xl font-extrabold uppercase tracking-widest text-on-surface">
          Changesets
        </h1>
        <Button variant="ghost" onClick={() => setImportOpen(true)}>
          Import changesets
        </Button>
      </div>

      {/* Summary progress */}
      <div className="mb-6">
        <ProgressBar value={pctMerged} className="mb-2" />
        <span className="font-mono text-xs text-on-surface-variant">
          {stats?.merged ?? 0} / {stats?.total ?? 0} merged ({pctMerged}%)
        </span>
      </div>

      {/* Burndown */}
      <BurndownChart batchChangeId={batchChangeId!} />

      {/* Bulk actions bar */}
      {selected.size > 0 && (
        <ChangesetBulkActions
          batchChangeId={batchChangeId!}
          selectedIds={[...selected]}
          onDone={() => setSelected(new Set())}
        />
      )}

      {/* Table */}
      <div className="mt-6 overflow-hidden">
        {items.map((cs, idx) => (
          <div
            key={cs.id}
            className={`flex items-center gap-4 px-4 py-3 border-b border-outline-variant/15 ${
              idx % 2 === 0 ? "bg-surface-container-low" : "bg-surface-container-lowest"
            }`}
          >
            <input
              type="checkbox"
              checked={selected.has(cs.id)}
              onChange={() => toggleSelect(cs.id)}
              className="accent-primary-container"
            />
            <TelemetryChip status={cs.state} />
            <span className="flex-1 font-mono text-sm text-on-surface">{cs.repo_ref}</span>
            <span className="font-body text-sm text-on-surface-variant truncate max-w-xs">
              {cs.title}
            </span>
            <TelemetryChip status={cs.review_state} />
            <TelemetryChip status={cs.ci_state} />
            {cs.external_url && (
              <a
                href={cs.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-xs text-primary hover:underline"
              >
                PR ↗
              </a>
            )}
          </div>
        ))}
        {items.length === 0 && (
          <p className="py-12 text-center font-mono text-sm text-on-surface-variant">
            No changesets yet. Apply the batch change to create them.
          </p>
        )}
      </div>

      <ImportChangesets
        open={importOpen}
        batchChangeId={batchChangeId!}
        onClose={() => setImportOpen(false)}
      />
    </div>
  );
}
