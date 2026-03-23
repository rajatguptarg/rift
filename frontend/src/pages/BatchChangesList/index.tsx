import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "../../components/ui/Button.tsx";
import { Card } from "../../components/ui/Card.tsx";
import { TelemetryChip } from "../../components/ui/TelemetryChip.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { api } from "../../services/api.ts";

interface BatchChange {
  id: string;
  name: string;
  description: string;
  state: string;
  created_at: string;
}

const STATE_FILTERS = ["ALL", "ACTIVE", "PREVIEW_RUNNING", "DRAFT", "ARCHIVED"];

export default function BatchChangesList() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState("ALL");

  const { data, isLoading } = useQuery({
    queryKey: ["batch-changes", activeFilter],
    queryFn: () =>
      api
        .get<{ items: BatchChange[] }>("/api/v1/batch-changes")
        .then((r) => r.data),
    staleTime: 30_000,
  });

  const items = data?.items ?? [];
  const filtered =
    activeFilter === "ALL" ? items : items.filter((b) => b.state === activeFilter);

  return (
    <div className="px-12 py-20">
      {/* Hero */}
      <div className="mb-16 flex items-start justify-between">
        <div>
          <h1 className="font-headline text-7xl font-extrabold uppercase tracking-widest text-on-surface leading-none">
            Batch
            <br />
            <span className="text-primary-container">Operations</span>
          </h1>
          <p className="mt-4 font-body text-on-surface-variant max-w-lg">
            Author, preview, and apply large-scale code changes across thousands of repositories.
          </p>
        </div>

        {/* Impact telemetry card */}
        <div className="rounded-none bg-secondary-fixed p-6 min-w-[200px]">
          <p className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">
            Active Changes
          </p>
          <p className="mt-2 font-headline text-5xl font-extrabold text-on-surface">
            {items.filter((b) => b.state === "ACTIVE").length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-8 flex gap-2">
        {STATE_FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            className={`rounded-full px-4 py-1.5 font-mono text-xs uppercase tracking-widest transition-colors ${
              activeFilter === f
                ? "bg-primary-container text-on-primary-container"
                : "bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            {f}
          </button>
        ))}
        <div className="flex-1" />
        <Button variant="primary" onClick={() => navigate("/batch-changes/new")}>
          + Create
        </Button>
      </div>

      {/* Grid */}
      {isLoading && (
        <div className="text-on-surface-variant font-mono text-sm">Loading...</div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map((bc) => (
          <Card
            key={bc.id}
            accent={bc.state === "ACTIVE"}
            onClick={() => navigate(`/batch-changes/${bc.id}`)}
          >
            <div className="mb-3 flex items-center justify-between">
              <TelemetryChip status={bc.state} />
              <span className="font-mono text-[10px] text-on-surface-variant">
                {new Date(bc.created_at).toLocaleDateString()}
              </span>
            </div>
            <h3 className="font-headline text-lg font-bold text-on-surface">{bc.name}</h3>
            <p className="mt-1 font-body text-sm text-on-surface-variant line-clamp-2">
              {bc.description}
            </p>
            {bc.state === "PREVIEW_RUNNING" && (
              <div className="mt-4">
                <ProgressBar value={45} />
              </div>
            )}
          </Card>
        ))}

        {!isLoading && filtered.length === 0 && (
          <div className="col-span-full py-20 text-center font-mono text-sm text-on-surface-variant">
            No batch changes found.
          </div>
        )}
      </div>
    </div>
  );
}
