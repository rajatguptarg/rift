import { Command } from "commander";
import { ApiClient } from "../client/api.js";

export function registerBatchApply(program: Command): void {
  program
    .command("batch apply")
    .description("Apply a batch change (trigger the apply workflow)")
    .requiredOption("--id <batchChangeId>", "Batch Change ID to apply")
    .option("-n, --namespace <ns>", "Target namespace")
    .option("--skip-errors", "Continue even if some workspaces fail", false)
    .action(async (opts) => {
      const client = ApiClient.fromConfig();

      console.log(`Applying batch change ${opts.id}...`);
      const run = await client.post<{ id: string; state: string }>(
        `/api/v1/batch-changes/${opts.id}/apply`,
        {}
      );

      console.log(JSON.stringify({ batchChangeId: opts.id, runId: run.id, state: run.state }, null, 2));
    });
}
