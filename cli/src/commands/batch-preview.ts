import { Command } from "commander";
import fs from "fs";
import { ApiClient } from "../client/api.js";

export function registerBatchPreview(program: Command): void {
  program
    .command("batch preview")
    .description("Run a preview for a batch spec file")
    .requiredOption("-f, --file <path>", "Path to batch spec YAML file")
    .option("-n, --namespace <ns>", "Target namespace")
    .option("--skip-errors", "Continue even if some workspaces fail", false)
    .action(async (opts) => {
      const specYaml = fs.readFileSync(opts.file as string, "utf-8");
      const client = ApiClient.fromConfig();

      console.log("Creating batch change...");
      const bc = await client.post<{ id: string; name: string }>("/api/v1/batch-changes", {
        namespace_id: opts.namespace ?? "default",
        name: `cli-preview-${Date.now()}`,
        description: "Created via CLI",
        source_mode: "CLI",
      });

      console.log(`Batch change created: ${bc.id}`);
      console.log("Uploading spec...");

      await client.post(`/api/v1/batch-changes/${bc.id}/spec`, {
        spec_yaml: specYaml,
        version: 0,
      });

      console.log("Starting preview...");
      const run = await client.post<{ id: string }>(`/api/v1/batch-changes/${bc.id}/preview`, {
        repo_refs: [],
        skip_errors: opts.skipErrors,
      });

      const previewUrl = `${process.env["RIFT_URL"] ?? "http://localhost:5173"}/batch-changes/${bc.id}/runs/${run.id}`;
      console.log(JSON.stringify({ batchChangeId: bc.id, runId: run.id, previewUrl }, null, 2));
    });
}
