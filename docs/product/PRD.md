---

# Product Requirements Document (PRD)
## Rift

**Document Version:** 1.0
**Date:** March 23, 2026
**Product:** Rift
---

## 1. Product Overview

Rift Batch Changes is a large-scale, cross-repository code automation tool that enables engineering teams to programmatically create, track, and manage code changes across hundreds or thousands of repositories simultaneously. Rather than opening pull requests manually one by one, engineers define a single declarative spec file (YAML), execute it against a search query that targets repositories, and Batch Changes handles the rest — creating branches, commits, pull requests, and tracking review/merge status across all affected repositories.

**Core Value Proposition:** Automate large-scale code changes — keep codebases up to date, fix critical security issues, and pay down tech debt across all repositories with a single declarative file.

---

## 2. Problem Statement

Large engineering organizations routinely face a class of problem that is impractical to solve manually: a single change needs to be applied across dozens, hundreds, or even thousands of repositories. Common examples include updating a deprecated API across all services, patching a critical CVE in a base Docker image, standardizing CI configuration, or migrating from one library to another. Doing this manually requires:

- Hunting down every affected repository
- Opening PRs one by one
- Tracking review and merge progress across each repo
- Re-running changes if reviewers request modifications

The time cost is prohibitive, the process is error-prone, and there is no unified visibility. Batch Changes eliminates this entire manual workflow.

---

## 3. Target Users & Personas

**Primary Persona — Platform/Infrastructure Engineer**
- Manages shared tooling, CI pipelines, base images, and build configurations
- Needs to push policy changes or dependency upgrades across all services simultaneously
- Values automation, auditability, and minimal manual intervention

**Secondary Persona — Security Engineer**
- Responds to CVEs and security advisories that affect multiple services
- Needs to refactor insecure function calls, pin image digests, or remove vulnerable packages at scale
- Requires speed (security patches are time-sensitive) and full coverage guarantees

**Tertiary Persona — Staff/Principal Engineer (Tech Debt Lead)**
- Drives deprecation of legacy APIs, library migrations, and codebase standardization efforts
- Needs language-aware tooling integration (e.g. Comby, sed, custom scripts) to handle syntactic transformations
- Values a clear burn-down view to track progress across a large migration

**Organizational Buyer — Director of Architecture / VP Engineering**
- Trusts the tool for impact assessment before changes are made
- Needs confidence in total blast radius visibility
- Justifies investment via time savings and reduced risk

---

## 4. Core Features

### 4.1 Declarative Batch Spec (YAML)
The centerpiece of the product. A batch spec is a YAML file that defines:
- `name` and `description` — human-readable identifier for the batch change
- `on` — a Rift search query that selects target repositories (e.g., `repositoriesMatchingQuery: file:README`)
- `steps` — a list of shell commands to run in each repo, inside a specified container image
- `changesetTemplate` — defines the title, body, branch name, and commit message for each generated pull request/merge request
- `workspaces` — optional monorepo support to target specific sub-projects within a single repo

This single file is the entire source of truth for a change campaign. It is version-controllable, reviewable, and repeatable.

### 4.2 Server-Side Execution (UI-Based)
Users can create and run batch changes directly from the Rift web UI without needing a local environment:
- Navigate to `/batch-changes` → click "Create batch change"
- Select from a library of curated templates or start from scratch
- Fill out template form fields (validated by regex)
- Name the batch change and optionally assign it to an org namespace
- Preview affected repositories and workspaces before execution
- Click "Run batch spec" to execute server-side
- Monitor real-time execution with per-workspace logs, step-level diffs, output variables, and execution timelines for debugging
- Review proposed diffs and click "Apply" to finalize

### 4.3 Local CLI Execution (rift CLI)
For advanced users preferring a local workflow:
- Install `rift` CLI (compatible binary served from the Rift instance itself)
- Authenticate via `rift login`
- Run `rift batch preview -f spec.yaml` to compute diffs and open a preview URL
- Run `rift batch apply -f spec.yaml` to apply without a preview (suitable for CI workflows)
- Supports `-skip-errors` flag to continue past individual repository failures
- Supports `-namespace` flag for org-namespaced batch changes

### 4.4 Changeset Management Dashboard
The primary UI surface after a batch change is created:
- Lists all changesets (PRs/MRs) grouped by the batch change, with real-time status
- **Status tracking:** Open, Closed, Merged per changeset
- **CI Checks:** Passed (green), Failed (red), Pending (yellow) per changeset
- **Review Status:** Approved, Changes Requested, Pending, or host-specific statuses
- **Burndown Chart:** Visual trend showing proportion of changesets merged over time since creation
- **Aggregate statistics:** Total batch changes, changesets merged, hours saved
- Filter and search across changesets
- Ability to publish, push, archive, or close individual or bulk changesets

### 4.5 Publish / Push Workflow
Before changesets exist on the code host, they are "unpublished" (preview-only, existing only in Rift). Users have explicit control over publication:
- **Publish:** Creates a PR/MR on the code host
- **Push:** Pushes a branch only (without creating a PR) — available on GitHub and GitLab
- **Draft Publish:** Creates a draft PR on hosts that support it
- Bulk publishing via multi-select in the UI

### 4.6 Code Host Compatibility
A single batch change can span multiple code hosts simultaneously:
- GitHub pull requests
- GitLab merge requests
- Bitbucket Server / Data Center pull requests
- Bitbucket Cloud pull requests
- Gerrit changes
- Perforce changelists (Beta)
- Phabricator diffs (planned)

### 4.7 Credential Management
- Users add personal access tokens per code host once (stored in Rift)
- Site admins can configure global credentials for the entire instance
- Credentials are scoped per user and per org

### 4.8 Namespace & Access Control
- Batch changes belong to a namespace (user or org)
- Users without read access to a specific repository see redacted info (no file paths, diffs, or repo names exposed)
- Batch changes can be shared via URL with anyone on the instance

### 4.9 Monorepo Support
- Use the `workspaces` key in a batch spec to target specific projects within a single repository
- Workspaces can be excluded individually from the preview

### 4.10 Template Library
- Site admins curate a library of batch spec templates for org-specific use cases
- Includes built-in examples (Configuration, Refactoring, Security)
- Templates use regex-validated form fields to fill batch spec parameters

### 4.11 Tracking Manually-Created Changesets
- Batch Changes can import and track changesets that were not created by Batch Changes itself
- Useful for managing migrations already in progress

---

## 5. Key Use Cases

**Configuration Management:** Edit every CI/CD, build config, and Dockerfile to alter steps, migrate versions, change base images. Example: update all Circle CI configs to use a new Docker Hub username.

**Code Refactoring:** Use language-aware tools (e.g. Comby) to perform structural code transformations across an entire language corpus. Example: replace `fmt.Sprintf("%d", v)` with `strconv.Itoa(v)` across all Go repositories.

**Security Patching:** Refactor insecure function calls, pin Docker image digests (replacing `:latest` with a fixed digest), or update vulnerable packages across hundreds of repositories at once.

---

## 6. User Flow

### Flow A: Creating a Batch Change via Server-Side UI

```
Entry Point
    └─ Navigate to /batch-changes (or click icon in top nav)
         └─ Click "Create batch change"
              └─ Template Selection Screen
                   ├─ Pick a curated template → Fill template form fields → Next
                   └─ Start from Scratch → Proceed to spec editor
                        └─ Name batch change + optionally set namespace → "Create"
                             └─ Batch Spec Editor + Right-Panel Preview
                                  ├─ Search preview resolves affected repos/workspaces
                                  ├─ Exclude individual workspaces if needed
                                  └─ Click "Run batch spec"
                                       └─ Execution Screen
                                            ├─ Real-time workspace status (logs, step diffs, output vars)
                                            └─ Execution complete → Proceed to "Batch Spec Preview"
                                                 └─ Review proposed diffs per repo
                                                      └─ Click "Apply"
                                                           └─ Batch Change Created
                                                                └─ Changeset Dashboard
                                                                     ├─ View status, CI, review state
                                                                     ├─ Select changesets → Publish
                                                                     │   ├─ Publish (creates PR)
                                                                     │   ├─ Publish as Draft
                                                                     │   └─ Push only (branch, no PR)
                                                                     └─ Monitor burn-down until all merged
```

### Flow B: Creating a Batch Change via CLI

```
Developer Terminal
    └─ Install rift CLI → rift login <instance-url>
         └─ Write batch spec YAML locally
              └─ rift batch preview -f spec.yaml
                   └─ Rift computes diffs → prints preview URL
                        └─ Open preview URL in browser
                             └─ Review proposed changes
                                  ├─ Looks good → click "Apply" in UI
                                  └─ Needs revision → edit YAML → re-run preview
                                       └─ Batch change created
                                            └─ Same publish/track flow as Flow A
```

### Flow C: CI/CD Continuous Update

```
CI Pipeline (e.g., GitHub Actions / Jenkins)
    └─ Trigger: merge to main / scheduled cron
         └─ rift batch apply -f spec.yaml (no preview step)
              └─ Batch change created/updated directly
                   └─ Changesets updated on all code hosts automatically
```

---

## 7. Design Language & Visual Identity

### 7.1 Color Palette
- **Background:** Pure black (`#000000`) — deep dark canvas dominates all hero and feature sections
- **Primary Accent:** Coral/Tomato Red (`#FF5543` approx.) — used for the primary CTA button ("Schedule a demo"), the announcement banner background, and logo star
- **Secondary Surface:** Very dark gray/charcoal (`#1A1A2E` or similar) — used for code snippet panels and testimonial cards
- **Text Primary:** White (`#FFFFFF`) — all headings on dark backgrounds
- **Text Secondary:** Light gray (`rgba(255,255,255,0.7)`) — subheading and body copy on dark backgrounds
- **Accent Purple:** Muted purple/violet — used on the "Batch Changes" pill/badge label in the hero
- **Code Theme:** Dark IDE-style color syntax highlighting — keywords in blue/teal, strings in green/yellow, comments in grey/green, variables in white. Consistent with VS Code dark theme conventions.
- **Active Tab Indicator:** White underline on active tab (Configuration, Refactoring, Security)

### 7.2 Typography
- **Display/Hero Headings:** Extra-bold, wide-tracking serif-adjacent grotesque. Very large size (~64-80px desktop). "Automate large-scale code changes" uses a two-line, center-aligned layout with extremely high font weight.
- **Body Copy:** Regular weight sans-serif, centered in hero, left-aligned in feature sections. Subheadings like "Change code everywhere with a single declarative file." use mixed bold + regular in a single sentence for emphasis.
- **Code Blocks:** Monospace font (Fira Code / JetBrains Mono style) with syntax highlighting, line numbers, consistent IDE aesthetic.
- **Navigation/Labels:** Clean, medium-weight sans-serif. Compact spacing.

### 7.3 Layout & Spacing
- Full-width sections with generous vertical padding
- Hero is centered, two-column feature sections (UI screenshot left / description right)
- Trust logo strip uses a horizontal, evenly spaced row with low-opacity grayscale logos that feel editorial
- Alternating dark and very dark section backgrounds create visual rhythm
- Grid/crosshatch subtle background texture visible in mid-page sections (dot/grid pattern) adds depth without distraction

### 7.4 Component Design
- **Primary Button:** White background, black text, heavily rounded pill shape. Bold, no icon. ("Schedule a demo")
- **Secondary Button:** Dark background, white text, rounded pill — same shape family. ("Pricing")
- **Primary CTA (nav):** Coral/tomato red fill, white text, rounded rectangle. ("Schedule a demo" in nav)
- **Pill Badge:** Small rounded tag with slight purple/dark fill and monospace text — "Batch Changes" hero label
- **Code Panels:** Dark card with rounded corners, line-number gutter, monospace code with full syntax highlighting. Embedded in a mock IDE chrome (with Batch Changes | Insights tabs visible at top of the mock UI screenshot)
- **Testimonial Card:** Dark rounded card with large quote text and attribution, set against a subtle grid background

### 7.5 Motion & Interactivity
- Tab switching (Configuration / Refactoring / Security) uses a smooth underline animation
- Minimal transitions — product is positioned as serious tooling, not flashy consumer software

### 7.6 Brand Voice & UX Copy
- Confident and technical, but not jargon-heavy in marketing copy
- Active imperatives: "Automate", "Change code everywhere", "Keep your code up to date"
- Quantified value: The UI screenshot shows real numbers: "124 batch changes", "5167 changesets merged", "1292.00 hours saved" — immediately communicating ROI
- Social proof positioned prominently: 13 recognizable enterprise logos (Indeed, Dropbox, Stripe, Uber, Atlassian, Reddit, Lyft, etc.) before any feature details
- Testimonial placed between trust logos and feature breakdown — classic SaaS conversion pattern

---

## 9. Technical Architecture (from Docs)

- **Batch Change Controller:** A reconciliation loop that continuously aligns the real state of changesets on code hosts with the desired state defined in the changeset specs
- **Changeset Spec:** Produced by executing the batch spec (running container commands on each matched repo), combining the resulting diffs with the changeset template to produce a list of changeset records
- **rift CLI:** Local or CI-triggered binary that executes container-based steps against matched repos, computes diffs, and uploads the resulting batch spec to the Rift API
- **Server-Side Execution:** Rift instance runs the containerized batch spec steps on its own infrastructure, enabling execution without a configured local environment
- **GraphQL API:** Full API access for programmatic management of batch changes


---

## 11. Non-Functional Requirements

- **Scalability:** Must handle batch changes targeting thousands of repositories across multiple code hosts simultaneously
- **Security:** Personal access tokens stored securely per user; fine-grained access control ensures users cannot see diffs from repositories they lack read access to; supports global admin-managed credentials
- **Auditability:** All batch spec executions are logged with step-level detail, output variables, and execution timelines
- **Reliability:** Execution continues past individual repository errors when `--skip-errors` flag is used; batch change controller continuously reconciles desired vs. actual state
- **CI/CD Integration:** `rift batch apply` can be embedded in CI pipelines for automated continuous change management without requiring UI interaction

---

## 12. Success Metrics

- **Efficiency:** Hours saved per batch change (surfaced natively in the dashboard — e.g., "1292 hours saved")
- **Adoption:** Number of batch changes created per month per organization
- **Coverage:** Changeset merge rate (burn-down chart slope — steeper = faster adoption)
- **Scale:** Average number of repositories per batch change
- **Reliability:** Percentage of batch spec executions that complete without errors
- **Conversion:** Demo request → paid enterprise conversion rate from the marketing landing page

---

## 13. Competitive Differentiation

Unlike generic scripting solutions or one-off migration scripts, Batch Changes provides a unified, auditable, UI-visible workflow that bridges the gap between code automation (scripting) and code review management (PR tracking). Competitors in adjacent spaces include OpenRewrite (JVM-focused AST refactoring), Dependabot (dependency-only), and manual scripting with GitHub's API. Batch Changes differentiates by being language-agnostic (any container, any tool), multi-code-host, and offering a full tracking and management UI rather than just automation.
