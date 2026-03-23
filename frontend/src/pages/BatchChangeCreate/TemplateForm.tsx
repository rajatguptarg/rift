import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Button } from "../../components/ui/Button.tsx";
import { api } from "../../services/api.ts";

interface FormField {
  name: string;
  label: string;
  field_type: string;
  required: boolean;
  default: string;
  options: string[];
}

interface TemplateFormProps {
  templateId: string;
  formSchema: FormField[];
  onCancel: () => void;
}

export const TemplateForm: React.FC<TemplateFormProps> = ({
  templateId,
  formSchema,
  onCancel,
}) => {
  const navigate = useNavigate();
  const [params, setParams] = useState<Record<string, string>>(
    Object.fromEntries(formSchema.map((f) => [f.name, f.default]))
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useMutation({
    mutationFn: () =>
      api
        .post(`/api/v1/templates/${templateId}/generate`, { params })
        .then((r) => r.data),
    onSuccess: (data: { spec_yaml: string }) => {
      // Navigate to spec editor with the generated YAML
      navigate(`/batch-changes/new?spec=${encodeURIComponent(data.spec_yaml)}`);
    },
    onError: (err: unknown) => {
      if (err && typeof err === "object" && "details" in err) {
        setErrors(err.details as Record<string, string>);
      }
    },
  });

  return (
    <div className="space-y-6">
      <h2 className="font-headline text-2xl font-bold uppercase tracking-widest text-on-surface">
        Configure Template
      </h2>

      {formSchema.map((field) => (
        <div key={field.name}>
          <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            {field.label}
            {field.required && <span className="ml-1 text-error">*</span>}
          </label>

          {field.field_type === "textarea" ? (
            <textarea
              required={field.required}
              value={params[field.name] ?? ""}
              onChange={(e) => setParams((p) => ({ ...p, [field.name]: e.target.value }))}
              rows={4}
              className="w-full rounded-none bg-surface-container px-4 py-2 font-mono text-sm text-on-surface outline-none ring-1 ring-outline-variant/20 focus:ring-primary/50 resize-none"
            />
          ) : field.field_type === "select" ? (
            <select
              value={params[field.name] ?? ""}
              onChange={(e) => setParams((p) => ({ ...p, [field.name]: e.target.value }))}
              className="w-full rounded-none bg-surface-container px-4 py-2 font-mono text-sm text-on-surface outline-none ring-1 ring-outline-variant/20"
            >
              {field.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          ) : (
            <input
              required={field.required}
              value={params[field.name] ?? ""}
              onChange={(e) => setParams((p) => ({ ...p, [field.name]: e.target.value }))}
              className="w-full rounded-none bg-surface-container px-4 py-2 font-mono text-sm text-on-surface outline-none ring-1 ring-outline-variant/20 focus:ring-primary/50"
            />
          )}

          {errors[field.name] && (
            <p className="mt-1 font-mono text-xs text-error">{errors[field.name]}</p>
          )}
        </div>
      ))}

      <div className="flex gap-3 pt-4">
        <Button
          variant="primary"
          disabled={mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? "Generating..." : "Use Template →"}
        </Button>
        <Button variant="ghost" onClick={onCancel}>
          Back
        </Button>
      </div>
    </div>
  );
};
