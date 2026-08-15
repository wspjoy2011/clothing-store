# CLAUDE.md

Working guidelines for the clothing-store codebase.

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

Conventional Commits, **one line**, no body: `type(scope): what was done`. Scope is the affected module (`cart`, `catalog`, `checkout`, `auth`, `backend`, `migrations`). Keep the summary short and concrete — `feat(cart): validate stock limit on quantity update`, not `feat(cart): improvements`.

## Dependencies

Backend dependencies are managed by **uv**: `pyproject.toml` + `uv.lock`, both committed. Add packages with `uv add`, install with `uv sync`.
