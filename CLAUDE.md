# CLAUDE.md

Working guidelines for the clothing-store codebase.

## Backend architecture

Request path: **route → controller → service → repository → DAO**. Each layer calls the next one only. No layer is skipped and none is called backwards.

- **Route** — HTTP surface: path, status codes, `Depends`. No logic.
- **Controller** — converts Schema ↔ DTO through `_convert_<src>_to_<dst>` helpers and maps domain exceptions to `HTTPException`.
- **Service** — business logic, and the only layer that opens a transaction boundary.
- **Repository** — SQL for one aggregate, returns DTOs.
- **DAO** — executes statements and reuses the connection of the active transaction.

**DTO inside, Schema at the edge.** DTOs are `@dataclass`, schemas are pydantic. A schema never travels deeper than the controller, a DTO never reaches the client, and the conversion lives nowhere else.

**Every dependency sits behind an `ABC`** in the module's `interfaces/` and is wired in its `dependencies.py`. Implementations are injected, never imported directly by their consumer.

**A module is a package** under `apps/<name>/`: `dto`, `exceptions`, `interfaces`, `repositories`, `schemas`, `services`, plus `controllers.py`, `routes.py`, `dependencies.py`. Reference: `apps/checkout`.

**Modules talk through service interfaces.** Reach another module by its `…ServiceInterface`, never by its repositories or tables.

**Transactions.** The service owns the boundary via `transaction_manager.atomic()`. A locking read (`SELECT … FOR UPDATE`) is valid only inside one — outside, the lock dies with the statement. Take the lock before reading anything the decision depends on.

**No ORM.** SQL is written by hand; schema changes ship as a migration.

**Errors.** Domain exceptions live in the module's `exceptions/`. Outward they describe the failed action, inward each layer logs what it alone knows.

## Comments and documentation

- **Zero comments in code by default.** All documentation lives in docstrings.
- Never write: restatements of the next line, change diaries (`# fixed`, `# was a JOIN before`), section headers inside a function body, or commented-out code.
- Unclear step → better name or extracted method, never a `#` line.
- Backend execution flow is traced with `logger.info` / `logger.warning`, not comments.

**Python — Google-style.** Docstring with `Args` / `Returns` / `Raises` on public methods of services, repositories, controllers and routes, and on abstract interface methods — the contract is documented on the `ABC`, the implementation repeats it. Service methods add a `Business logic: ...` line after the summary. One-liners are fine for trivial methods. Reference: `apps/checkout/services/cart.py`.

**JavaScript / Vue — JSDoc.** On every exported service method and every composable, including nested helpers. No TypeScript here, so `@param {Type}` / `@returns {Type}` carry real type information. Reference: `composables/cart/useCartFormatting.js`, `services/cartService.js`.

**One exception — section markers.** A one-word divider (`# Products`, `// State`, `<!-- Error State -->`) is allowed only to group entries in a declarative list: path dictionaries, config fields, `__all__`, a composable's returned object, `<template>` sections. Never inside a function body.

**Language.** Code, docstrings, comments, logs and commit messages — English only.

## Commits

Conventional Commits, **one line**, no body: `type(scope): what was done`.

The scope is mandatory — never commit a bare `docs:`, `fix:` or `chore:`. It names the affected module: `cart`, `catalog`, `checkout`, `auth`, `db`, `accounts`, `backend`, `frontend`, `migrations`, `tests`.

Keep the summary short and concrete: `feat(cart): validate stock limit on quantity update`, not `feat(cart): improvements`.

## Tests

Every change ships with tests. A bug fix adds a test that fails without the fix; new logic is covered by tests for its behaviour, not its implementation.

Prove every new test by mutation before considering it done: break the code it covers, watch it go red for the right reason, restore the code, watch it go green. A test that stays green against broken code certifies nothing.

Backend tests live in `services/backend/tests`, mirror the package they cover and run with `pytest`. External boundaries — database, SMTP, HTTP — are replaced by fakes, so no test needs a running Postgres or `.env`. One behaviour per test, named as the statement it proves.

Coverage is measured with `pytest --cov`. The target is **90%**; `fail_under` in `pyproject.toml` holds the floor at the level already reached, so a change that drops coverage fails the run rather than relying on anyone noticing. Raise the floor when you raise the coverage. Chase uncovered branches, not uncovered lines: a file at 100% whose error paths were never executed is not covered.

## Dependencies

Backend dependencies are managed by **uv**: `pyproject.toml` + `uv.lock`, both committed. Add packages with `uv add`, install with `uv sync`.
