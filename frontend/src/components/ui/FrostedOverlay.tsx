import React from "react";
import clsx from "clsx";

interface FrostedOverlayProps {
  open: boolean;
  onClose?: () => void;
  children?: React.ReactNode;
  className?: string;
}

export const FrostedOverlay: React.FC<FrostedOverlayProps> = ({
  open,
  onClose,
  children,
  className,
}) => {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-background/60 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Panel */}
      <div
        className={clsx(
          "relative rounded-none bg-surface-container-high/60 backdrop-blur-xl",
          "shadow-[0_0_64px_rgba(255,180,169,0.05)]",
          "p-8 min-w-[480px] max-w-2xl w-full",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
};
