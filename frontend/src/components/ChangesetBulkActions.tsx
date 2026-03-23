import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "./ui/Button.tsx";
import { FrostedOverlay } from "./ui/FrostedOverlay.tsx";
import { api } from "../services/api.ts";

interface ChangesetBulkActionsProps {
  batchChangeId: string;
  selectedIds: string[];
  onDone: () => void;
}

const PUBLISH_MODES = [
  { value: "FULL_PR", label: "Full PR" },
  { value: "DRAFT_PR", label: "Draft PR" },
  { value: "PUSH_ONLY", label: "Push Only" },
];

export const ChangesetBulkActions: React.FC<ChangesetBulkActionsProps> = ({
  batchChangeId,
  selectedIds,
  onDone,
}) => {
  const [mode, setMode] = useState("FULL_PR");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const qc = useQueryClient();

  const publishMutation = useMutation({
    mutationFn: () =>
      api
        .post(`/api/v1/batch-changes/${batchChangeId}/changesets/publish`, {
          publish_mode: mode,
          changeset_ids: selectedIds,
        })
        .then((r) => r.data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["changesets", batchChangeId] });
      setConfirmOpen(false);
      onDone();
    },
  });

  return (
    <>
      <div className="mb-4 flex items-center gap-3 rounded-none bg-surface-container px-4 py-3">
        <span className="font-mono text-xs text-on-surface-variant">
          {selectedIds.length} selected
        </span>
        <div className="flex gap-1">
          {PUBLISH_MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => setMode(m.value)}
              className={`rounded-full px-3 py-1 font-mono text-xs transition-colors ${
                mode === m.value
                  ? "bg-primary-container text-on-primary-container"
                  : "border border-outline-variant/20 text-primary hover:bg-surface-container-high"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setConfirmOpen(true)}
        >
          Publish
        </Button>
      </div>

      <FrostedOverlay open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <h2 className="mb-4 font-headline text-xl font-bold text-on-surface">
          Publish {selectedIds.length} Changeset{selectedIds.length !== 1 ? "s" : ""}?
        </h2>
        <p className="mb-2 font-body text-sm text-on-surface-variant">
          Mode:{" "}
          <span className="font-mono text-xs text-primary">
            {PUBLISH_MODES.find((m) => m.value === mode)?.label}
          </span>
        </p>
        <p className="mb-6 font-body text-sm text-on-surface-variant">
          This will create pull requests on the code host. Are you sure?
        </p>
        <div className="flex gap-3">
          <Button
            variant="primary"
            size="sm"
            disabled={publishMutation.isPending}
            onClick={() => publishMutation.mutate()}
          >
            {publishMutation.isPending ? "Publishing..." : "Confirm"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setConfirmOpen(false)}
          >
            Cancel
          </Button>
        </div>
      </FrostedOverlay>
    </>
  );
};
