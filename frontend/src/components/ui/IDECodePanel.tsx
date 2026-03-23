import React from "react";
import clsx from "clsx";

interface IDECodePanelProps {
  children?: React.ReactNode;
  className?: string;
  language?: string;
}

export const IDECodePanel: React.FC<IDECodePanelProps> = ({
  children,
  className,
  language = "yaml",
}) => {
  return (
    <div
      className={clsx(
        "relative overflow-auto rounded-none bg-surface-container-lowest crosshatch-bg scrollbar-thin font-mono text-sm text-on-surface",
        className
      )}
      style={{ scrollbarWidth: "thin", scrollbarColor: "#353535 #131313" }}
      data-language={language}
    >
      <div className="p-4">{children}</div>

      <style>{`
        .syntax-keyword { color: #45D8ED; }
        .syntax-string   { color: #A5D6FF; }
        .syntax-key      { color: #FFB4A9; }
        .syntax-comment  { color: #5B403C; font-style: italic; }
      `}</style>
    </div>
  );
};
