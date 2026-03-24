# rift Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-24

## Active Technologies
- Python 3.12 (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic, Motor, python-jose, passlib[bcrypt], React 18, React Router 6, TanStack Query, axios (003-restore-auth-access)
- MongoDB for user records and audit events; JWT bearer token held in browser auth state/local storage; existing Redis/Temporal/storage stack unchanged for this feature (003-restore-auth-access)

- Python 3.12 (backend), TypeScript 5.x / React 18 (frontend)
- FastAPI, Motor, python-jose, passlib[bcrypt], React Router 6, TanStack Query, axios
- MongoDB for users and roles, browser local storage for the bearer token, existing Redis and object storage unchanged for this feature

## Project Structure

```text
backend/
frontend/
cli/
docs/
specs/
```

## Commands

- `make infra-up`
- `make dev-backend`
- `make dev-frontend`
- `make docker-up-build`
- `make test-backend`
- `make test-frontend`
- `make test`
- `make lint`
- `make format`

## Code Style

- Backend: keep FastAPI code layered as API -> services -> adapters -> models.
- Backend: use Pydantic models for request/response and domain validation.
- Frontend: keep route-level code in `frontend/src/pages`, shared UI in `frontend/src/components`, and API access in `frontend/src/services`.
- Frontend auth work should keep public auth routes outside the protected application shell.

## Recent Changes
- 003-restore-auth-access: Added Python 3.12 (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic, Motor, python-jose, passlib[bcrypt], React 18, React Router 6, TanStack Query, axios

- 003-restore-auth-access: planned first-party web authentication, Mongo-backed users, public auth routes, and a bootstrapped local super user

## Development Instructions

- You must update the documentation, README, api, contracts, anything related to changes after making the change and keep the documentation up-to-date.
- You must update README after every change. README should contain about the project, how to install, develop locally, run and test it. It should contain instructuons on how to contribute, the architecture of the project.
- You must create a adr with naming convention `adr-xxx-title` under the `docs/adr` folder for making architectural decisions.

## Commit Instructions
**How to Write Commit Messages**

We follow the **Conventional Commits** format with a **mandatory Jira ticket reference**. This keeps history readable, enables automation like changelogs and releases, and makes traceability explicit.

**Format**

Every commit message must follow this structure:

```
type(scope?): subject [XYZ-123]
```

• `type` is required
• `scope` is optional
• `subject` is required
• `Jira ticket` is required and must be at the end

No trailing period. Keep everything on a single line.

**Types**

Use one of the following types:

* `feat` – new user facing functionality
* `fix` – bug fix
* `docs` – documentation only changes
* `style` – formatting, whitespace, linting (no logic change)
* `refactor` – code change that is neither a fix nor a feature
* `perf` – performance improvement
* `test` – adding or updating tests
* `build` – build system or dependency changes
* `ci` – CI or pipeline related changes
* `chore` – maintenance tasks, tooling, cleanup
* `revert` – revert a previous commit

**Scope**

The scope describes the area affected by the change. Use short, clear names such as a service, module, or domain.

Examples:

```
fix(auth): handle expired tokens [PAY-431]
feat(api): add pagination support [CORE-982]
chore(ci): update node version [PLAT-117]
```

Do not use ticket numbers as scopes.

**Subject**

The subject should be:

* Written in **imperative mood** (think: “this commit will…”)
* Short and clear, ideally under 72 characters
* Lowercase, no period at the end

Good examples:

```
fix(server): send cors headers [XYZ-123]
feat(blog): add comment section [BLOG-88]
chore(deps): update commitlint [DEV-241]
```

Bad examples:

```
XYZ-123 fix server bug
fix(server): fixed cors issue [XYZ-123]
feat: Added pagination [XYZ-123].
```

**Jira Ticket Rules**

* The ticket must be in the format `PROJECT-123`
* Place it **at the end of the message in square brackets**
* One primary ticket per commit
* If multiple tickets are involved, split the work into separate commits

**General Rules**

* One logical change per commit
* Do not combine unrelated changes under one ticket
* Avoid vague subjects like “update stuff” or “misc changes”
* If a change is hard to describe clearly, the commit is probably too large

**Why This Matters**

This format allows us to:

* Link code changes directly to Jira issues
* Enforce consistency with commitlint
* Generate changelogs automatically
* Make reviews, rollbacks, and audits easier

Commits that do not follow this format will fail validation.

## Pull request instructions

**How to Create a Pull Request**

We use pull requests to review, discuss, and safely merge changes. Follow these rules to keep reviews fast and predictable.

**Before Opening a PR**

Make sure the following are true before you open a pull request:

* Your branch is up to date with the target branch (usually `main` or `master`)
* All commits follow the agreed commit message format, including the Jira ticket
* The code builds successfully
* Tests are added or updated where relevant
* Linting and formatting checks pass locally

Do not open a PR that is known to be broken.

**Branch Naming**

Name your branch using this pattern:

```
<type>/<jira-ticket>-short-description
```

Examples:

```
feat/XYZ-123-add-pagination
fix/PAY-431-handle-expired-tokens
chore/PLAT-117-update-node
```

**PR Title**

The PR title should:

* Clearly describe the change
* Include the Jira ticket number
* Be written in plain, descriptive language

Good examples:

```
Add pagination to transactions API [XYZ-123]
Fix CORS headers for auth service [PAY-431]
Update Node.js version used in CI [PLAT-117]
```

Avoid vague titles like “Fix bug” or “Updates”.

**PR Description**

Every PR must include the following sections.

**What does this change do?**

Briefly explain the problem and the solution. Focus on intent, not implementation details.

**Why is this change needed?**

Explain the context. Link to the Jira ticket and mention any relevant background.

**How was this tested?**

Describe how you validated the change. Examples:

* Unit tests added or updated
* Manual testing steps
* CI checks relied upon

If no tests were added, explain why.

**Checklist**

Before requesting review, confirm:

* [ ] Code follows project standards
* [ ] Tests added or updated
* [ ] Documentation updated if needed
* [ ] No unrelated changes included
* [ ] Jira ticket linked and up to date

**PR Size and Scope**

* Keep PRs focused on one logical change
* Avoid mixing refactors with feature work
* If a PR grows too large, split it

Smaller PRs are reviewed faster and merged more safely.

**Review and Approval**

* Assign the appropriate reviewers
* Address feedback promptly and clearly
* Do not force push after review unless explicitly requested
* Re-request review after making significant changes

**Merging**

* Ensure all required checks pass
* Resolve all review comments
* Use the approved merge strategy for the repo
* Delete the branch after merge

PRs that do not follow these rules may be sent back for rework.
