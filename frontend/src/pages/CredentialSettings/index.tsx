import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "../../components/ui/Card.tsx";
import { TelemetryChip } from "../../components/ui/TelemetryChip.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { FrostedOverlay } from "../../components/ui/FrostedOverlay.tsx";
import { api } from "../../services/api.ts";

interface Credential {
  id: string;
  code_host_id: string;
  scope: string;
  scopes: string[];
  created_at: string;
}

export default function CredentialSettings() {
  const [addOpen, setAddOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [form, setForm] = useState({ code_host_id: "", secret: "", scope: "USER" });

  const { data: credentials, refetch } = useQuery({
    queryKey: ["credentials"],
    queryFn: () =>
      api.get<Credential[]>("/api/v1/credentials").then((r) => r.data),
  });

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/v1/credentials", {
      ...form,
      namespace_id: "default",
    });
    setAddOpen(false);
    setForm({ code_host_id: "", secret: "", scope: "USER" });
    void refetch();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await api.delete(`/api/v1/credentials/${deleteTarget}`);
    setDeleteTarget(null);
    void refetch();
  };

  return (
    <div className="px-12 py-12">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-headline text-4xl font-extrabold uppercase tracking-widest text-on-surface">
          Credentials
        </h1>
        <Button variant="primary" onClick={() => setAddOpen(true)}>
          + Add Credential
        </Button>
      </div>

      <div className="space-y-4">
        {(credentials ?? []).map((cred) => (
          <Card key={cred.id}>
            <div className="flex items-center gap-4">
              <TelemetryChip status={cred.code_host_id.toUpperCase()} />
              <span className="font-mono text-xs text-on-surface-variant">
                SCOPE:{cred.scope}
              </span>
              <span className="font-mono text-xs text-on-surface-variant flex-1">
                {cred.id}
              </span>
              <span className="font-mono text-xs text-on-surface-variant">
                {new Date(cred.created_at).toLocaleDateString()}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDeleteTarget(cred.id)}
              >
                Delete
              </Button>
            </div>
          </Card>
        ))}

        {(credentials ?? []).length === 0 && (
          <p className="py-12 text-center font-mono text-sm text-on-surface-variant">
            No credentials configured.
          </p>
        )}
      </div>

      {/* Add credential overlay */}
      <FrostedOverlay open={addOpen} onClose={() => setAddOpen(false)}>
        <h2 className="mb-6 font-headline text-2xl font-bold uppercase tracking-widest text-on-surface">
          Add Credential
        </h2>
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
              Code Host ID
            </label>
            <input
              required
              value={form.code_host_id}
              onChange={(e) => setForm((f) => ({ ...f, code_host_id: e.target.value }))}
              className="w-full rounded-none bg-surface-container px-4 py-2 font-body text-on-surface outline-none ring-1 ring-outline-variant/20"
              placeholder="github"
            />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs uppercase tracking-widest text-on-surface-variant">
              Token
            </label>
            <input
              required
              type="password"
              value={form.secret}
              onChange={(e) => setForm((f) => ({ ...f, secret: e.target.value }))}
              className="w-full rounded-none bg-surface-container px-4 py-2 font-body text-on-surface outline-none ring-1 ring-outline-variant/20"
              placeholder="ghp_..."
            />
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="submit" variant="primary" size="sm">
              Save
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setAddOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </FrostedOverlay>

      {/* Delete confirmation overlay */}
      <FrostedOverlay open={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
        <h2 className="mb-4 font-headline text-xl font-bold text-on-surface">
          Delete Credential?
        </h2>
        <p className="mb-6 font-body text-sm text-on-surface-variant">
          This action cannot be undone. Any batch changes using this credential may fail.
        </p>
        <div className="flex gap-3">
          <Button variant="primary" size="sm" onClick={handleDelete}>
            Delete
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setDeleteTarget(null)}>
            Cancel
          </Button>
        </div>
      </FrostedOverlay>
    </div>
  );
}
