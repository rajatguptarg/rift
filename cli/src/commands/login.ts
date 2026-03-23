import { Command } from "commander";
import readline from "readline";
import { ApiClient } from "../client/api.js";

export function registerLogin(program: Command): void {
  program
    .command("login")
    .description("Authenticate with a Rift instance")
    .option("--url <url>", "Rift API URL", "http://localhost:8000")
    .option("--token <token>", "API token (or input interactively)")
    .action(async (opts) => {
      let token: string = opts.token as string;
      if (!token) {
        token = await promptToken();
      }
      try {
        const client = new ApiClient(opts.url as string, token);
        await client.get("/health");
        ApiClient.saveCredentials(opts.url as string, token);
        console.log(`✓ Logged in to ${opts.url}`);
      } catch (err) {
        console.error("Login failed:", err);
        process.exit(1);
      }
    });
}

function promptToken(): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stderr });
  return new Promise((resolve) => {
    rl.question("Enter API token: ", (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}
