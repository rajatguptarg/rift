// Shared TypeScript type definitions derived from the API contract

export interface BatchChange {
  id: string;
  namespace_id: string;
  name: string;
  description: string;
  source_mode: "UI" | "CLI";
  state:
    | "DRAFT"
    | "PREVIEW_RUNNING"
    | "PREVIEW_READY"
    | "APPLYING"
    | "ACTIVE"
    | "PAUSED"
    | "ARCHIVED"
    | "FAILED";
  created_by: string;
  active_spec_id: string | null;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
  version: number;
}

export interface BatchSpec {
  id: string;
  batch_change_id: string;
  spec_yaml: string;
  spec_hash: string;
  search_query: string;
  created_at: string;
}

export interface BatchRun {
  id: string;
  batch_change_id: string;
  batch_spec_id: string;
  state: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";
  total_workspaces: number;
  completed_workspaces: number;
  failed_workspaces: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface WorkspaceExecution {
  id: string;
  batch_run_id: string;
  repo_ref: string;
  state: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "SKIPPED" | "CANCELLED";
  duration_seconds: number | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  is_excluded: boolean;
}

export interface Changeset {
  id: string;
  changeset_spec_id: string;
  batch_change_id: string;
  repo_ref: string;
  external_url: string | null;
  state: "UNPUBLISHED" | "OPEN" | "DRAFT" | "MERGED" | "CLOSED" | "ARCHIVED";
  title: string;
  branch: string;
  review_state: "PENDING" | "APPROVED" | "CHANGES_REQUESTED";
  ci_state: "PENDING" | "RUNNING" | "PASSED" | "FAILED" | "SKIPPED";
  created_at: string;
  updated_at: string;
  merged_at: string | null;
}

export interface Credential {
  id: string;
  namespace_id: string;
  user_id: string | null;
  code_host_id: string;
  scope: "GLOBAL" | "ORG" | "USER";
  scopes: string[];
  created_at: string;
  rotated_at: string | null;
}

export interface Template {
  id: string;
  namespace_id: string | null;
  name: string;
  description: string;
  category: string;
  form_schema: FormField[];
  validation_rules: Record<string, string>;
  is_builtin: boolean;
  is_active: boolean;
}

export interface FormField {
  name: string;
  label: string;
  field_type: string;
  required: boolean;
  default: string;
  options: string[];
}

export interface CursorPage<T> {
  items: T[];
  next_cursor: string | null;
  total: number | null;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, string>;
  };
}

// ── Auth / Session types (from auth-api.yaml contract) ────────────────────

export type AccessRole = "SUPER_USER" | "STANDARD";

export interface UserSummary {
  id: string;
  username: string;
  display_name: string;
  email: string | null;
  role: AccessRole;
  bootstrap_managed: boolean;
  created_at: string;
}

export interface AuthSessionResponse {
  access_token: string;
  token_type: "Bearer";
  expires_at: string;
  user: UserSummary;
}

export interface SignInRequest {
  username: string;
  password: string;
}

export interface SignUpRequest {
  username: string;
  display_name: string;
  email?: string;
  password: string;
}

export interface CurrentUserResponse {
  user: UserSummary;
}
