import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { FrostedOverlay } from "../../components/ui/FrostedOverlay.tsx";
import { IDECodePanel } from "../../components/ui/IDECodePanel.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { api } from "../../services/api.ts";

interface ImportChangesetsProps {
  open: boolean;
  batchChangeId: string;
  onClose: () => void;
}

export const ImportChangesets: React.FC<ImportChangesetsProps> = ({
  open,
  batchChangeId,
  onClose,
}) => {
  const [urlsText, setUrlsText] = useState("");
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => {
      const urls = urlsText
        .split("\n")
        .map((u) => u.trim())
        .filter(Boolean);
      return api
        .post(`/api/v1/batch-changes/${batchChangeId}/changesets/import`, { urls })
        .then((r) => r.data);
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["changesets", batchChangeId] });
      onClose();
    },
  });

  return (
    <FrostedOverlay open={open} onClose={onClose}>
      <h2 className="mb-6 font-headline text-2xl font-bold uppercase tracking-widest text-on-surface">
        Import Changesets
      </h2>
      <p className="mb-4 font-body text-sm text-on-surface-variant">
        Paste one PR/MR URL per line to import externally-created changesets.
      </p>
      <IDECodePanel className="mb-4 h-40">
        <textarea
          value={urlsText}
          onChange={(e) => setUrlsText(e.target.value)}
          className="h-full w-full resize-none bg-transparent font-mono text-sm text-on-surface outline-none"
          placeholder="https://github.com/acme/service-a/pull/42&#10;https://github.com/acme/service-b/pull/17"
        />
      </IDECodePanel>
      <div className="flex gap-3">
        <Button
          variant="primary"
          disabled={mutation.isPending || !urlsText.trim()}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? "Importing..." : "Import"}
        </Button>
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
      </div>
    </FrostedOverlay>
  );
};
