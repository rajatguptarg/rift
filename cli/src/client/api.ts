import fs from "fs";
import os from "os";
import path from "path";
import fetch from "node-fetch";

const CONFIG_PATH = path.join(os.homedir(), ".rift", "config.json");

interface Config {
  apiUrl: string;
  token: string;
}

function loadConfig(): Config | null {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
    return JSON.parse(raw) as Config;
  } catch {
    return null;
  }
}

function saveConfig(config: Config): void {
  const dir = path.dirname(CONFIG_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), { mode: 0o600 });
}

export class ApiClient {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string, token: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.token = token;
  }

  static fromConfig(): ApiClient {
    const cfg = loadConfig();
    if (!cfg) {
      throw new Error(
        "Not logged in. Run `rift login` first."
      );
    }
    return new ApiClient(cfg.apiUrl, cfg.token);
  }

  static saveCredentials(apiUrl: string, token: string): void {
    saveConfig({ apiUrl, token });
  }

  async get<T>(path: string): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      headers: this._headers(),
    });
    if (!resp.ok) {
      throw new Error(`GET ${path} failed: ${resp.status} ${resp.statusText}`);
    }
    return resp.json() as Promise<T>;
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: { ...this._headers(), "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`POST ${path} failed: ${resp.status} — ${text}`);
    }
    return resp.json() as Promise<T>;
  }

  private _headers(): Record<string, string> {
    return { Authorization: `Bearer ${this.token}` };
  }
}
