import React from "react";
import { Button } from "../ui/Button";

export interface AuthField {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  autoComplete?: string;
}

interface AuthFormProps {
  fields: AuthField[];
  submitLabel: string;
  onSubmit: (values: Record<string, string>) => Promise<void>;
  error?: string | null;
  footer?: React.ReactNode;
}

export const AuthForm: React.FC<AuthFormProps> = ({
  fields,
  submitLabel,
  onSubmit,
  error,
  footer,
}) => {
  const [values, setValues] = React.useState<Record<string, string>>(() =>
    Object.fromEntries(fields.map((f) => [f.name, ""]))
  );
  const [loading, setLoading] = React.useState(false);

  const handleChange = (name: string, value: string) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(values);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {fields.map((field) => (
        <div key={field.name}>
          <label
            htmlFor={field.name}
            className="mb-1 block font-mono text-xs uppercase tracking-wider text-on-surface-variant"
          >
            {field.label}
          </label>
          <input
            id={field.name}
            name={field.name}
            type={field.type ?? "text"}
            required={field.required ?? true}
            minLength={field.minLength}
            maxLength={field.maxLength}
            pattern={field.pattern}
            autoComplete={field.autoComplete}
            value={values[field.name]}
            onChange={(e) => handleChange(field.name, e.target.value)}
            className="w-full rounded border border-outline bg-surface px-3 py-2 font-mono text-sm text-on-surface placeholder-on-surface-variant focus:border-primary focus:outline-none"
          />
        </div>
      ))}
      {error && (
        <p role="alert" className="font-mono text-xs text-error">
          {error}
        </p>
      )}
      <Button type="submit" variant="primary" className="w-full" disabled={loading}>
        {loading ? "..." : submitLabel}
      </Button>
      {footer && <div className="mt-4 text-center">{footer}</div>}
    </form>
  );
};
