import React from "react";
import clsx from "clsx";

type ChipStatus =
  | "RUNNING"
  | "FAILED"
  | "OPEN"
  | "LIVE"
  | "SYNCING"
  | "MERGED"
  | "CLOSED"
  | "DRAFT"
  | "UNPUBLISHED"
  | "ARCHIVED"
  | string;

const STATUS_STYLES: Record<string, string> = {
  RUNNING: "bg-tertiary-container text-on-tertiary-container",
  FAILED: "bg-error-container text-on-error-container",
  OPEN: "bg-primary-container text-on-primary-container",
  LIVE: "bg-primary-container text-on-primary-container",
  SYNCING: "bg-secondary-container text-secondary",
  MERGED: "bg-primary-container text-on-primary-container",
  CLOSED: "bg-surface-container-highest text-on-surface-variant",
  DRAFT: "bg-secondary-container text-secondary",
  UNPUBLISHED: "bg-surface-container-high text-on-surface-variant",
  ARCHIVED: "bg-surface-container text-on-surface-variant",
};

interface TelemetryChipProps {
  status: ChipStatus;
  className?: string;
}

export const TelemetryChip: React.FC<TelemetryChipProps> = ({ status, className }) => {
  const style = STATUS_STYLES[status] ?? "bg-surface-container text-on-surface-variant";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-tighter",
        style,
        className
      )}
    >
      <span
        className={clsx(
          "h-1.5 w-1.5 rounded-full",
          status === "RUNNING" ? "animate-pulse bg-current" : "bg-current opacity-70"
        )}
      />
      {status}
    </span>
  );
};
