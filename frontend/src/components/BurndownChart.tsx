import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api.ts";

interface BurndownEntry {
  date: string;
  total: number;
  merged: number;
  open: number;
  closed: number;
}

interface BurndownChartProps {
  batchChangeId: string;
}

export const BurndownChart: React.FC<BurndownChartProps> = ({ batchChangeId }) => {
  const { data } = useQuery({
    queryKey: ["burndown", batchChangeId],
    queryFn: () =>
      api
        .get<{ data: BurndownEntry[] }>(`/api/v1/batch-changes/${batchChangeId}/burndown`)
        .then((r) => r.data),
    staleTime: 60_000,
  });

  const entries = data?.data ?? [];
  if (entries.length === 0) return null;

  const maxValue = Math.max(...entries.map((e) => e.total), 1);
  const width = 600;
  const height = 120;
  const padding = 32;

  const points = entries.map((e, i) => {
    const x = padding + (i / (entries.length - 1)) * (width - padding * 2);
    const y = height - padding - (e.merged / maxValue) * (height - padding * 2);
    return `${x},${y}`;
  });
  const polyline = points.join(" ");

  // Fill polygon
  const firstX = padding;
  const lastX = padding + (width - padding * 2);
  const bottomY = height - padding;
  const polygon = `${firstX},${bottomY} ${polyline} ${lastX},${bottomY}`;

  return (
    <div className="mb-8 rounded-none bg-surface-container-lowest p-4">
      <p className="mb-3 font-mono text-xs uppercase tracking-widest text-on-surface-variant">
        Merge Burndown (30d)
      </p>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        preserveAspectRatio="none"
      >
        {/* Fill */}
        <polygon points={polygon} fill="#FF5543" fillOpacity={0.15} />
        {/* Line */}
        <polyline
          points={polyline}
          fill="none"
          stroke="#FF5543"
          strokeWidth={2}
        />
      </svg>
      {/* Axis labels */}
      <div className="mt-2 flex justify-between font-mono text-[10px] text-on-surface-variant">
        <span>{entries[0]?.date}</span>
        <span>{entries[entries.length - 1]?.date}</span>
      </div>
    </div>
  );
};
