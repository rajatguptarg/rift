import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "../../components/ui/Card.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { TelemetryChip } from "../../components/ui/TelemetryChip.tsx";

const BUILT_IN_TEMPLATES = [
  {
    id: "builtin-add-license",
    name: "Add LICENSE file",
    description: "Add an MIT, Apache-2.0, or GPLv3 license file to all matching repositories.",
    category: "COMPLIANCE",
  },
  {
    id: "builtin-update-deps",
    name: "Update dependencies",
    description: "Bump all outdated npm or pip dependencies to their latest versions.",
    category: "MAINTENANCE",
  },
  {
    id: "builtin-add-ci",
    name: "Add GitHub Actions CI",
    description: "Add a standard CI pipeline workflow file to all repositories.",
    category: "CI/CD",
  },
];

interface TemplateSelectorProps {
  onSelect: (templateId: string | null) => void;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({ onSelect }) => {
  return (
    <div className="space-y-4">
      <h2 className="font-headline text-2xl font-bold uppercase tracking-widest text-on-surface">
        Choose a Starting Point
      </h2>

      {/* Start from scratch */}
      <Card onClick={() => onSelect(null)}>
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-3xl text-primary-container">
            add_circle
          </span>
          <div>
            <h3 className="font-headline text-lg font-bold text-on-surface">
              Start from Scratch
            </h3>
            <p className="font-body text-sm text-on-surface-variant">
              Write your own batch spec YAML.
            </p>
          </div>
        </div>
      </Card>

      <div className="mt-6">
        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-on-surface-variant">
          Templates
        </p>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {BUILT_IN_TEMPLATES.map((tpl) => (
            <Card key={tpl.id} onClick={() => onSelect(tpl.id)}>
              <div className="mb-2 flex items-center justify-between">
                <TelemetryChip status={tpl.category} />
              </div>
              <h3 className="font-headline text-base font-bold text-on-surface">{tpl.name}</h3>
              <p className="mt-1 font-body text-sm text-on-surface-variant">
                {tpl.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
