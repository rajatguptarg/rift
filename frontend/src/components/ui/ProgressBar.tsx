import React from "react";
import clsx from "clsx";

interface ProgressBarProps {
  value: number; // 0–100
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ value, className }) => {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div
      className={clsx(
        "h-1 w-full overflow-hidden rounded-full bg-surface-container-highest",
        className
      )}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full rounded-full bg-primary-container transition-all duration-1000"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
};
