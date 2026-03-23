import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { IDECodePanel } from "../../components/ui/IDECodePanel.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { api } from "../../services/api.ts";

const EXAMPLE_SPEC = `name: example-batch-change
description: Add a CONTRIBUTING.md file to all repos

on:
  - repositoriesMatchingQuery: "repo:acme/ archived:no"

steps:
  - run: |
      if [ ! -f CONTRIBUTING.md ]; then
        cat > CONTRIBUTING.md << 'EOF'
# Contributing
Thank you for contributing!
EOF
      fi

changesetTemplate:
  title: Add CONTRIBUTING.md
  body: Adds a standard CONTRIBUTING.md file.
  branch: add-contributing-md
  commit:
    message: "chore: add CONTRIBUTING.md"
`;

export default function BatchSpecEditor() {
  const { id: batchChangeId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [specYaml, setSpecYaml] = useState(EXAMPLE_SPEC);

  const saveMutation = useMutation({
    mutationFn: () =>
      api
        .patch(`/api/v1/batch-changes/${batchChangeId}/spec`, {
          spec_yaml: specYaml,
          version: 0,
        })
        .then((r) => r.data),
  });

  const previewMutation = useMutation({
    mutationFn: () =>
      api
        .post(`/api/v1/batch-changes/${batchChangeId}/preview`, {
          repo_refs: [],
          skip_errors: false,
        })
        .then((r) => r.data),
    onSuccess: (run: { id: string }) => {
      navigate(`/batch-changes/${batchChangeId}/runs/${run.id}`);
    },
  });

  const handleRunPreview = async () => {
    await saveMutation.mutateAsync();
    previewMutation.mutate();
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Left 65% — YAML editor */}
      <div className="flex w-[65%] flex-col border-r border-surface-container">
        <div className="flex items-center justify-between border-b border-surface-container px-6 py-3">
          <span className="font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            batch_spec.yaml
          </span>
          <Button
            variant="primary"
            size="sm"
            onClick={handleRunPreview}
            disabled={previewMutation.isPending || saveMutation.isPending}
          >
            {previewMutation.isPending ? "Starting..." : "Run Batch Spec ▶"}
          </Button>
        </div>
        <IDECodePanel className="flex-1 overflow-auto">
          <textarea
            value={specYaml}
            onChange={(e) => setSpecYaml(e.target.value)}
            className="h-full w-full resize-none bg-transparent font-mono text-sm text-on-surface outline-none"
            spellCheck={false}
          />
        </IDECodePanel>
      </div>

      {/* Right 35% — preview panel */}
      <div className="flex w-[35%] flex-col bg-surface-container">
        <div className="border-b border-surface-container-high px-6 py-3">
          <span className="font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            Resolved Repositories
          </span>
        </div>
        <div className="flex-1 overflow-auto px-6 py-4">
          <p className="font-body text-sm text-on-surface-variant">
            Run the spec to preview matching repositories.
          </p>
          {previewMutation.isError && (
            <p className="mt-4 font-mono text-xs text-error">
              Preview failed. Check your spec and try again.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
