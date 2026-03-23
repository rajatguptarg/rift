import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Button } from "../../components/ui/Button.tsx";
import { api } from "../../services/api.ts";

export default function BatchChangeCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    description: "",
    namespace_id: "default",
  });

  const mutation = useMutation({
    mutationFn: () =>
      api.post("/api/v1/batch-changes", { ...form, source_mode: "UI" }).then((r) => r.data),
    onSuccess: (bc: { id: string }) => {
      navigate(`/batch-changes/${bc.id}/spec`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    mutation.mutate();
  };

  return (
    <div className="mx-auto max-w-2xl px-12 py-20">
      <h1 className="mb-2 font-headline text-5xl font-extrabold uppercase tracking-widest text-on-surface">
        New Batch Change
      </h1>
      <p className="mb-12 font-body text-on-surface-variant">
        Create a batch change to run a spec across your repositories.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name */}
        <div>
          <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            Name
          </label>
          <input
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
            className="w-full rounded-none bg-surface-container px-4 py-3 font-body text-on-surface outline-none ring-1 ring-outline-variant/20 focus:ring-primary/50"
            placeholder="e.g. add-lint-rules"
          />
        </div>

        {/* Description */}
        <div>
          <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            Description
          </label>
          <textarea
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            rows={3}
            className="w-full rounded-none bg-surface-container px-4 py-3 font-body text-on-surface outline-none ring-1 ring-outline-variant/20 focus:ring-primary/50 resize-none"
            placeholder="What does this batch change do?"
          />
        </div>

        {/* Namespace */}
        <div>
          <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
            Namespace
          </label>
          <input
            value={form.namespace_id}
            onChange={(e) => setForm((f) => ({ ...f, namespace_id: e.target.value }))}
            className="w-full rounded-none bg-surface-container px-4 py-3 font-body text-on-surface outline-none ring-1 ring-outline-variant/20 focus:ring-primary/50"
            placeholder="default"
          />
        </div>

        {mutation.isError && (
          <p className="font-mono text-xs text-error">
            Failed to create batch change. Please try again.
          </p>
        )}

        <div className="flex gap-4 pt-4">
          <Button
            type="submit"
            variant="primary"
            disabled={mutation.isPending || !form.name.trim()}
          >
            {mutation.isPending ? "Creating..." : "Continue to Spec Editor →"}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate("/batch-changes")}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
