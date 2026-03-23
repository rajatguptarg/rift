#!/usr/bin/env node
import { Command } from "commander";
import { registerLogin } from "./commands/login.js";
import { registerBatchPreview } from "./commands/batch-preview.js";
import { registerBatchApply } from "./commands/batch-apply.js";

const program = new Command();

program
  .name("rift")
  .description("Rift Batch Changes CLI")
  .version("0.1.0");

registerLogin(program);
registerBatchPreview(program);
registerBatchApply(program);

program.parse(process.argv);
