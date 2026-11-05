# AGENTS.md

## 1. Scope and source of guidance

These instructions apply to the `backend/` directory: the IF Explore API, which
keeps a local copy of the library collection synced from the campus PHL catalog.
The project uses Python 3.12+ (CI runs 3.14), Django 5.2 LTS, Django Ninja, and
SQLite with FTS5. Check `requirements.txt` before assuming a library is
available.

Use [docs/project-guidelines.md](docs/project-guidelines.md) as the source for
organization, data, and API conventions. This file summarizes the operational
rules to follow while working. Setup, commands, environment variables, and the
API reference live in [README.md](README.md).

The frontend has its own instructions in `frontend/AGENTS.md`. The API contract
is shared: changing it means changing both sides (see the guidelines, §7).

## 2. Mandatory rules

1. Preserve the existing settings, security, migrations, and CI configuration.
2. Do not use `Any`, `# type: ignore`, or `cast` to hide type errors in
   application code. Tests may use `# type: ignore[method-assign]` to replace a
   client method with a fake.
3. Keep modules, functions, and services cohesive, with clear responsibilities.
4. Do not create apps, layers, or abstractions without a concrete need. The
   Django ORM is the data access layer: no repositories on top of it.
5. Keep business rules out of routes, commands, and admin classes.
6. Do not introduce dependencies without a clear technical justification. Pin
   new ones in `requirements.txt`. `phl_client/` must keep using only the
   standard library.
7. Preserve existing behavior unless a change is requested.
8. Treat external data as untrusted: PHL pages, request parameters, and request
   bodies are validated at the boundary.
9. Never expose or store who borrowed a book. The PHL copy page shows the
   borrower's registration number; application code must never call
   `copies(..., include_borrower=True)`, and fixtures must not contain real ones.
10. Be gentle with the PHL server: it is a campus CGI that starts one process
    per request. Do not add per-title loops over the collection, keep the pause
    between requests, and state the number of requests a change adds.
11. Never put secrets in code or fixtures. Configuration comes from environment
    variables (`config/settings.py`), optionally through `backend/.env`.

## 3. Working in the repository

Run commands from `backend/` with the virtual environment active (see
`README.md`).

Before implementing:

1. Read this file and `docs/project-guidelines.md`.
2. Inspect the relevant modules, services, tests, and fixtures.
3. Look for existing services, parsers, and helpers that can be reused.
4. Choose the smallest complete change that satisfies the requirement.

During implementation:

- Make focused changes and preserve unrelated work.
- Follow the patterns already used in the repository.
- Use English for identifiers, module names, and file names (PEP 8:
  `snake_case` modules and functions, `PascalCase` classes).
- Write docstrings and explanatory comments in Brazilian Portuguese (`pt-BR`),
  using the Google style sections (`Args:`, `Returns:`, `Raises:`). Do not
  comment trivial code.
- Add type hints to every function and method.
- Prefer pure functions for rules that do not need the database (see
  `catalog/services/classification.py`), so they can be tested without it.
- Generate migrations with `makemigrations`; never edit an applied migration.
- Do not access the real PHL catalog in tests.

Before completing:

1. Review the diff for unnecessary complexity or out-of-scope changes.
2. Run the checks the CI runs:
   `python manage.py check`, `python manage.py makemigrations --check --dry-run`,
   and `python manage.py test`.
3. When a change touches the PHL client or the sync, also try it once against
   the real catalog when it is reachable, and say so.
4. Clearly report checks that ran, failed, or could not be run. There is no
   linter or type checker configured in the project; do not claim one passed.
5. Update `README.md`, `.env.example`, or the guidelines when a command,
   variable, endpoint, or convention changes.

Never claim that a command, test, or verification passed unless it was run.

## 4. Language, security, and dependencies

- Messages shown to people (API error details, admin labels, command output)
  are in Brazilian Portuguese; identifiers are in English.
- Catalog labels that are data (area names, document types, languages) stay as
  the catalog writes them.
- Remember that settings read from the environment may be missing or wrong:
  keep safe defaults for development and fail clearly in production
  (`DJANGO_SECRET_KEY` with `DJANGO_DEBUG=false`).
- Do not weaken security settings, validation, or tests to make a change pass.

## 5. Definition of done

An implementation is complete when it:

- satisfies the requested requirement;
- preserves types, module boundaries, the API contract, and project conventions;
- introduces no unjustified abstractions or dependencies;
- keeps the load on the PHL server known and small;
- includes tests for new rules and regressions, without network access;
- passes the CI checks, or reports their limitations;
- updates the documentation it affects;
- contains no unrelated changes.
