import React from "react";
import clsx from "clsx";

interface ContentShellProps {
  children?: React.ReactNode;
  className?: string;
}

export const ContentShell: React.FC<ContentShellProps> = ({
  children,
  className,
}) => {
  return (
    <main
      className={clsx(
        "ml-64 min-h-screen bg-black pt-16",
        className
      )}
    >
      {children}
    </main>
  );
};
