import React from "react";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title,
  subtitle,
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="font-mono text-2xl font-bold uppercase tracking-widest text-on-surface">
            RIFT
          </h1>
          <p className="mt-1 font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            Batch Changes Platform
          </p>
        </div>
        <div className="rounded-lg border border-outline-variant bg-surface-container-low p-8">
          <h2 className="mb-1 font-mono text-base font-semibold uppercase tracking-wider text-on-surface">
            {title}
          </h2>
          {subtitle && (
            <p className="mb-6 font-mono text-xs text-on-surface-variant">
              {subtitle}
            </p>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};
